const API_URL = "http://localhost:8000";

export interface Document {
    url: string;
    name: string;
}

export interface ChatResponse {
    answer: string;
    code: string | null;
}

export interface ExecuteResponse {
    output?: string;
    error?: string;
}

export const api = {
    async getHealth() {
        const res = await fetch(`${API_URL}/health`);
        return res.json();
    },

    async getDocuments() {
        const res = await fetch(`${API_URL}/documents`);
        const data = await res.json();
        return data.documents as Document[];
    },

    async ingestPdf(url: string) {
        const res = await fetch(`${API_URL}/ingest`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Ingestion failed");
        }
        return res.json();
    },

    async chat(query: string) {
        const res = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Chat failed");
        }
        return res.json() as Promise<ChatResponse>;
    },

    async executeCode(code: string) {
        const res = await fetch(`${API_URL}/execute`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Execution failed");
        }
        return res.json() as Promise<ExecuteResponse>;
    }
};
