package cache

import (
	"context"
	"encoding/json"
	"log"
	"time"

	"github.com/redis/go-redis/v9"
)

type RedisCache struct {
	client    *redis.Client
	ctx       context.Context
	defaultTTL time.Duration
}

type CacheConfig struct {
	Addr     string
	Password string
	DB       int
	TTL      time.Duration
}

func NewRedisCache(config CacheConfig) *RedisCache {
	client := redis.NewClient(&redis.Options{
		Addr:     config.Addr,
		Password: config.Password,
		DB:       config.DB,
	})

	ctx := context.Background()

	// Test connection
	_, err := client.Ping(ctx).Result()
	if err != nil {
		log.Printf("Warning: Redis connection failed: %v", err)
		log.Println("Falling back to in-memory cache")
		return nil
	}

	log.Println("Connected to Redis")
	return &RedisCache{
		client:    client,
		ctx:       ctx,
		defaultTTL: config.TTL,
	}
}

// Get retrieves value from Redis
func (c *RedisCache) Get(key string, dest interface{}) bool {
	if c == nil || c.client == nil {
		return false
	}

	val, err := c.client.Get(c.ctx, key).Result()
	if err != nil {
		return false
	}

	if err := json.Unmarshal([]byte(val), dest); err != nil {
		return false
	}

	return true
}

// Set stores value in Redis
func (c *RedisCache) Set(key string, value interface{}, ttl ...time.Duration) {
	if c == nil || c.client == nil {
		return
	}

	data, err := json.Marshal(value)
	if err != nil {
		return
	}

	duration := c.defaultTTL
	if len(ttl) > 0 {
		duration = ttl[0]
	}

	c.client.Set(c.ctx, key, data, duration)
}

// Delete removes value from Redis
func (c *RedisCache) Delete(key string) {
	if c == nil || c.client == nil {
		return
	}

	c.client.Del(c.ctx, key)
}

// DeletePattern removes all keys matching pattern
func (c *RedisCache) DeletePattern(pattern string) {
	if c == nil || c.client == nil {
		return
	}

	iter := c.client.Scan(c.ctx, 0, pattern, 100).Iterator()
	for iter.Next(c.ctx) {
		c.client.Del(c.ctx, iter.Val())
	}
}

// Clear removes all keys
func (c *RedisCache) Clear() {
	if c == nil || c.client == nil {
		return
	}

	c.client.FlushAll(c.ctx)
}

// GetStats returns Redis stats
func (c *RedisCache) GetStats() map[string]interface{} {
	if c == nil || c.client == nil {
		return map[string]interface{}{"status": "disconnected"}
	}

	info, err := c.client.Info(c.ctx, "stats", "memory").Result()
	if err != nil {
		return map[string]interface{}{"error": err.Error()}
	}

	dbSize, _ := c.client.DBSize(c.ctx).Result()

	return map[string]interface{}{
		"status":   "connected",
		"db_size":  dbSize,
		"info":     info,
	}
}

// GetOrSet retrieves from cache or executes function
func (c *RedisCache) GetOrSet(key string, fn func() (interface{}, error), ttl ...time.Duration) (interface{}, error) {
	var result interface{}
	if c.Get(key, &result) {
		return result, nil
	}

	value, err := fn()
	if err != nil {
		return nil, err
	}

	c.Set(key, value, ttl...)
	return value, nil
}

// PipelineGet retrieves multiple keys at once
func (c *RedisCache) PipelineGet(keys []string) map[string]interface{} {
	result := make(map[string]interface{})

	if c == nil || c.client == nil {
		return result
	}

	pipe := c.client.Pipeline()
	cmds := make(map[string]*redis.StringCmd)

	for _, key := range keys {
		cmds[key] = pipe.Get(c.ctx, key)
	}

	pipe.Exec(c.ctx)

	for key, cmd := range cmds {
		val, err := cmd.Result()
		if err != nil {
			continue
		}

		var data interface{}
		if err := json.Unmarshal([]byte(val), &data); err == nil {
			result[key] = data
		}
	}

	return result
}

// PipelineSet stores multiple keys at once
func (c *RedisCache) PipelineSet(items map[string]interface{}, ttl ...time.Duration) {
	if c == nil || c.client == nil {
		return
	}

	pipe := c.client.Pipeline()
	duration := c.defaultTTL
	if len(ttl) > 0 {
		duration = ttl[0]
	}

	for key, value := range items {
		data, _ := json.Marshal(value)
		pipe.Set(c.ctx, key, data, duration)
	}

	pipe.Exec(c.ctx)
}

// Increment increments a counter
func (c *RedisCache) Increment(key string) int64 {
	if c == nil || c.client == nil {
		return 0
	}

	val, _ := c.client.Incr(c.ctx, key).Result()
	return val
}

// SetEx sets value with expiry
func (c *RedisCache) SetEx(key string, value interface{}, ttl time.Duration) {
	c.Set(key, value, ttl)
}

// Exists checks if key exists
func (c *RedisCache) Exists(key string) bool {
	if c == nil || c.client == nil {
		return false
	}

	val, _ := c.client.Exists(c.ctx, key).Result()
	return val > 0
}

// TTL returns remaining TTL
func (c *RedisCache) TTL(key string) time.Duration {
	if c == nil || c.client == nil {
		return 0
	}

	val, _ := c.client.TTL(c.ctx, key).Result()
	return val
}
