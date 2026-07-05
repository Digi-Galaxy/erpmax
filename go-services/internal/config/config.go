package config

import (
	"os"
	"strconv"
)

type Config struct {
	Port          int
	DBHost        string
	DBPort        int
	DBUser        string
	DBPassword    string
	DBName        string
	RedisAddr     string
	RedisPassword string
	RedisDB       int
	WorkerCount   int
	BatchSize     int
	CacheTTL      int
	MaxRetries    int
	UploadDir     string
}

func Load() *Config {
	return &Config{
		Port:          getEnvInt("PORT", 8080),
		DBHost:        getEnv("DB_HOST", "localhost"),
		DBPort:        getEnvInt("DB_PORT", 3306),
		DBUser:        getEnv("DB_USER", "root"),
		DBPassword:    getEnv("DB_PASSWORD", ""),
		DBName:        getEnv("DB_NAME", "erpmax"),
		RedisAddr:     getEnv("REDIS_ADDR", "localhost:6379"),
		RedisPassword: getEnv("REDIS_PASSWORD", ""),
		RedisDB:       getEnvInt("REDIS_DB", 0),
		WorkerCount:   getEnvInt("WORKER_COUNT", 10),
		BatchSize:     getEnvInt("BATCH_SIZE", 1000),
		CacheTTL:      getEnvInt("CACHE_TTL", 3600),
		MaxRetries:    getEnvInt("MAX_RETRIES", 3),
		UploadDir:     getEnv("UPLOAD_DIR", "/tmp/erpmax/files"),
	}
}

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value, exists := os.LookupEnv(key); exists {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}
