// Command server is the HTTP backend for the web UI.
package main

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"os"

	"github.com/RafeSymonds/space_traders_monolith/internal/spacetraders"
)

const apiURL = "https://api.spacetraders.io/v2"

func main() {
	addr := os.Getenv("ADDR")
	if addr == "" {
		addr = "127.0.0.1:8080"
	}

	client, err := spacetraders.NewClientWithResponses(apiURL)
	if err != nil {
		slog.Error("create spacetraders client", "err", err)
		os.Exit(1)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/status", func(w http.ResponseWriter, r *http.Request) {
		resp, err := client.GetStatusWithResponse(r.Context())
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadGateway)
			return
		}
		if resp.JSON200 == nil {
			http.Error(w, "unexpected status "+resp.Status(), http.StatusBadGateway)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(resp.JSON200); err != nil {
			slog.Error("encode status", "err", err)
		}
	})

	slog.Info("listening", "addr", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		slog.Error("server stopped", "err", err)
		os.Exit(1)
	}
}
