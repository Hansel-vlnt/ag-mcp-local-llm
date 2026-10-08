# Rencana Arsitektur Sistem: Antigravity Local LLM MCP Bridge

Dokumen ini adalah cetak biru teknis (blueprint) untuk membangun repositori **`local-llm-mcp`**. Proyek ini berfungsi sebagai jembatan (bridge) berbasis **Model Context Protocol (MCP)** yang menghubungkan **Antigravity (Google Gemini Cloud)** dengan **Local LLM (Ollama)** yang berjalan di GPU lokal (NVIDIA GeForce RTX 5060, 8GB VRAM).

---

## 1. Tujuan Proyek

1. **Hemat Kuota Cloud (Zero Quota Offloading):** Mendelegasikan tugas komputasi berat, pemrosesan file teks panjang, log parsing, atau draf kode ke Local LLM tanpa memakan kuota token Gemini.
2. **Hybrid Intelligence Workflow:** Antigravity bertindak sebagai *Orchestrator* (pemikir & pengarah tugas), sedangkan Local LLM bertindak sebagai *Sub-Agent/Worker* (eksekutor tugas lokal).
3. **Standar Terbuka (Universal MCP):** Dibuat menggunakan standar Model Context Protocol resmi sehingga dapat dipublikasikan ke GitHub dan kompatibel tidak hanya dengan Antigravity, tetapi juga dengan Claude Desktop, Cursor, dll.

---

## 2. Diagram Arsitektur Sistem

```mermaid
flowchart TD
    subgraph Cloud["1. Cloud Layer (Google)"]
        User([User]) -->|Chat / Request| AG[Antigravity Agent / Gemini]
    end

    subgraph Host["2. Local Host (Windows Machine)"]
        AG -->|Stdio Protocol (MCP)| Server["MCP Server (local-llm-mcp/server.py)"]
        Server -->|HTTP POST /api/generate| Ollama["Ollama Engine (Port 11434)"]
        
        subgraph Hardware["3. Akselerasi Perangkat Keras"]
            Ollama -->|CUDA Inference| GPU["NVIDIA GeForce RTX 5060 (8GB VRAM)"]
        end

        Ollama -->|Stream / Result JSON| Server
        Server -->|Tool Result Text| AG
    end

    AG -->|Jawaban Terpadu / Final Response| User
```

---

## 3. Spesifikasi Teknis Lingkungan

* **Sistem Operasi:** Windows 11 (64-bit)
* **Python Runtime:** Python 3.14+
* **Akselerasi GPU:** NVIDIA GeForce RTX 5060 Laptop GPU (8.0 GiB VRAM, Compute 12.0)
* **Local Inference Engine:** Ollama (Service default pada `http://127.0.0.1:11434`)
* **Protokol:** MCP SDK (`mcp` library dengan FastMCP) melalui transport `stdio`

---

## 4. Struktur Direktori Repositori (`local-llm-mcp`)

```text
local-llm-mcp/
├── ARCHITECTURE_PLAN.md    # Dokumen blueprint ini
├── README.md               # Dokumentasi instalasi & panduan penggunaan GitHub
├── requirements.txt        # Dependensi: mcp, httpx, pydantic
├── .env.example            # Contoh konfigurasi environment
├── src/
│   ├── __init__.py
│   ├── config.py           # Konfigurasi endpoint Ollama & default model
│   ├── client.py           # HTTP Client asinkron ke Ollama REST API
│   └── server.py           # Entry point FastMCP server yang mengekspos tools
└── tests/
    └── test_connection.py  # Skrip pengujian mandiri koneksi Ollama & MCP
```

---

## 5. Rencana MCP Tools yang Diekspos ke Antigravity

Server MCP ini akan mengekspos beberapa tool yang dapat langsung dipanggil oleh Antigravity:

| Nama Tool | Parameter | Deskripsi Fungsi |
| :--- | :--- | :--- |
| `ask_local_llm` | `prompt: str`, `model: str = "default"` | Mengirim prompt komputasi berat ke local LLM dan menerima respons/feedback. |
| `analyze_file_locally` | `file_path: str`, `instruction: str` | Membaca file lokal berukuran besar langsung di mesin dan menganalisisnya tanpa mengirim isi file ke cloud. |
| `check_local_llm_status` | *None* | Memeriksa ketersediaan Ollama, status GPU, serta daftar model yang sudah terunduh. |

---

## 6. Rencana Konfigurasi Antigravity (`mcp_config.json`)

Setelah server MCP selesai dibuat, server akan didaftarkan ke `C:\Users\harla\.gemini\config\mcp_config.json`:

```json
{
  "mcpServers": {
    "local-llm-worker": {
      "command": "python",
      "args": [
        "C:\\Users\\harla\\local-llm-mcp\\src\\server.py"
      ],
      "env": {
        "OLLAMA_HOST": "http://127.0.0.1:11434",
        "DEFAULT_MODEL": "qwen2.5-coder:7b"
      }
    }
  }
}
```

---

## 7. Roadmap Pelaksanaan Bertahap

### Fase 1: Setup Workspace & Lingkungan
1. Buka folder `C:\Users\harla\local-llm-mcp` sebagai workspace di sesi chat baru.
2. Inisialisasi Git repository (`git init`).
3. Setup virtual environment Python dan instal dependensi (`mcp[cli]`, `httpx`).

### Fase 2: Implementasi Server FastMCP
1. Buat `src/config.py` dan `src/client.py` untuk membungkus komunikasi ke Ollama API.
2. Buat `src/server.py` menggunakan FastMCP dengan tool `ask_local_llm` dan `check_local_llm_status`.
3. Buat skrip pengujian cepat `tests/test_connection.py`.

### Fase 3: Integrasi Sistem Antigravity
1. Daftarkan konfigurasi ke `C:\Users\harla\.gemini\config\mcp_config.json`.
2. Verifikasi discovery tool di Antigravity.

### Fase 4: Pemilihan Model Optimal & Uji Coba Delegasi
1. Unduh model koding yang optimal untuk VRAM 8GB (rekomendasi: `qwen2.5-coder:7b` atau sejenisnya).
2. Lakukan uji coba delegasi: Antigravity memberikan instruksi refactoring, Local LLM memprosesnya, dan mengembalikan feedback ke Antigravity.

---

## 8. Panduan Prompt untuk Memulai di Chat Baru

Ketika Anda membuat sesi chat baru dengan folder `C:\Users\harla\local-llm-mcp` sebagai active workspace, Anda cukup menyalin (copy-paste) prompt berikut:

> *"Halo! Saya membuka workspace `local-llm-mcp`. Silakan baca file `ARCHITECTURE_PLAN.md` yang sudah disiapkan di folder ini, lalu mari kita mulai implementasi Fase 1 dan Fase 2."*
