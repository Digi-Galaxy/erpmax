package services

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

type WebSocketService struct {
	clients    map[*Client]bool
	broadcast  chan []byte
	register   chan *Client
	unregister chan *Client
	mu         sync.RWMutex
}

type Client struct {
	conn     *websocket.Conn
	send     chan []byte
	rooms    map[string]bool
	userID   string
}

type WSMessage struct {
	Type    string      `json:"type"`
	Room    string      `json:"room,omitempty"`
	Data    interface{} `json:"data"`
	UserID  string      `json:"user_id,omitempty"`
	Time    time.Time   `json:"time"`
}

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func NewWebSocketService() *WebSocketService {
	return &WebSocketService{
		clients:    make(map[*Client]bool),
		broadcast:  make(chan []byte, 256),
		register:   make(chan *Client),
		unregister: make(chan *Client),
	}
}

// Start starts the WebSocket service
func (ws *WebSocketService) Start() {
	go ws.run()
	log.Println("WebSocket service started")
}

// HandleWebSocket handles WebSocket connections
func (ws *WebSocketService) HandleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}

	client := &Client{
		conn:   conn,
		send:   make(chan []byte, 256),
		rooms:  make(map[string]bool),
		userID: r.URL.Query().Get("user_id"),
	}

	ws.register <- client

	go client.writePump()
	go client.readPump(ws)
}

// Broadcast sends message to all clients
func (ws *WebSocketService) Broadcast(message []byte) {
	ws.broadcast <- message
}

// BroadcastToRoom sends message to all clients in a room
func (ws *WebSocketService) BroadcastToRoom(room string, message []byte) {
	ws.mu.RLock()
	defer ws.mu.RUnlock()

	msg := WSMessage{
		Type: "room_message",
		Room: room,
		Data: json.RawMessage(message),
		Time: time.Now(),
	}

	data, _ := json.Marshal(msg)

	for client := range ws.clients {
		if client.rooms[room] {
			select {
			case client.send <- data:
			default:
				close(client.send)
				delete(ws.clients, client)
			}
		}
	}
}

// SendToUser sends message to specific user
func (ws *WebSocketService) SendToUser(userID string, message []byte) {
	ws.mu.RLock()
	defer ws.mu.RUnlock()

	for client := range ws.clients {
		if client.userID == userID {
			select {
			case client.send <- message:
			default:
				close(client.send)
				delete(ws.clients, client)
			}
		}
	}
}

// JoinRoom adds client to a room
func (ws *WebSocketService) JoinRoom(client *Client, room string) {
	ws.mu.Lock()
	defer ws.mu.Unlock()

	client.rooms[room] = true

	// Notify room
	notify := WSMessage{
		Type:   "user_joined",
		Room:   room,
		UserID: client.userID,
		Time:   time.Now(),
	}
	data, _ := json.Marshal(notify)

	for c := range ws.clients {
		if c.rooms[room] && c != client {
			select {
			case c.send <- data:
			default:
			}
		}
	}
}

// LeaveRoom removes client from a room
func (ws *WebSocketService) LeaveRoom(client *Client, room string) {
	ws.mu.Lock()
	defer ws.mu.Unlock()

	delete(client.rooms, room)

	// Notify room
	notify := WSMessage{
		Type:   "user_left",
		Room:   room,
		UserID: client.userID,
		Time:   time.Now(),
	}
	data, _ := json.Marshal(notify)

	for c := range ws.clients {
		if c.rooms[room] {
			select {
			case c.send <- data:
			default:
			}
		}
	}
}

// GetConnectedUsers returns list of connected users
func (ws *WebSocketService) GetConnectedUsers() []string {
	ws.mu.RLock()
	defer ws.mu.RUnlock()

	users := make(map[string]bool)
	for client := range ws.clients {
		if client.userID != "" {
			users[client.userID] = true
		}
	}

	result := make([]string, 0, len(users))
	for user := range users {
		result = append(result, user)
	}

	return result
}

// GetRoomUsers returns list of users in a room
func (ws *WebSocketService) GetRoomUsers(room string) []string {
	ws.mu.RLock()
	defer ws.mu.RUnlock()

	users := make(map[string]bool)
	for client := range ws.clients {
		if client.rooms[room] && client.userID != "" {
			users[client.userID] = true
		}
	}

	result := make([]string, 0, len(users))
	for user := range users {
		result = append(result, user)
	}

	return result
}

func (ws *WebSocketService) run() {
	for {
		select {
		case client := <-ws.register:
			ws.mu.Lock()
			ws.clients[client] = true
			ws.mu.Unlock()

			log.Printf("Client connected: %s", client.userID)

		case client := <-ws.unregister:
			ws.mu.Lock()
			if _, ok := ws.clients[client]; ok {
				delete(ws.clients, client)
				close(client.send)
			}
			ws.mu.Unlock()

			log.Printf("Client disconnected: %s", client.userID)

		case message := <-ws.broadcast:
			ws.mu.RLock()
			for client := range ws.clients {
				select {
				case client.send <- message:
				default:
					close(client.send)
					delete(ws.clients, client)
				}
			}
			ws.mu.RUnlock()
		}
	}
}

func (c *Client) readPump(ws *WebSocketService) {
	defer func() {
		ws.unregister <- c
		c.conn.Close()
	}()

	for {
		_, message, err := c.conn.ReadMessage()
		if err != nil {
			break
		}

		var msg WSMessage
		if err := json.Unmarshal(message, &msg); err != nil {
			continue
		}

		switch msg.Type {
		case "join_room":
			if room, ok := msg.Data.(string); ok {
				ws.JoinRoom(c, room)
			}
		case "leave_room":
			if room, ok := msg.Data.(string); ok {
				ws.LeaveRoom(c, room)
			}
		case "room_message":
			if room := msg.Room; room != "" {
				ws.BroadcastToRoom(room, message)
			}
		}
	}
}

func (c *Client) writePump() {
	ticker := time.NewTicker(30 * time.Second)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if !ok {
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			w, err := c.conn.NextWriter(websocket.TextMessage)
			if err != nil {
				return
			}
			w.Write(message)

			n := len(c.send)
			for i := 0; i < n; i++ {
				w.Write([]byte("\n"))
				w.Write(<-c.send)
			}

			if err := w.Close(); err != nil {
				return
			}

		case <-ticker.C:
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}
