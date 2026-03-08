import { useState, useEffect } from "react";
import { Search, Plus, FileText, Loader2, Link as LinkIcon } from "lucide-react";
import { api, Document } from "../api";
import { toast } from "sonner";

interface LeftSidebarProps {
    onSelectDoc: (doc: Document) => void;
}

export function LeftSidebar({ onSelectDoc }: LeftSidebarProps) {
    const [docs, setDocs] = useState<Document[]>([]);
    const [url, setUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(true);

    useEffect(() => {
        fetchDocs();
    }, []);

    const fetchDocs = async () => {
        try {
            const data = await api.getDocuments();
            setDocs(data);
        } catch (err) {
            console.error(err);
        } finally {
            setFetching(false);
        }
    };

    const handleIngest = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url.trim()) return;

        setLoading(true);
        const toastId = toast.loading("Ingesting PDF...");

        try {
            const result = await api.ingestPdf(url);
            toast.success(result.message, { id: toastId });
            setUrl("");
            fetchDocs();
        } catch (err: any) {
            toast.error(err.message || "Ingestion failed", { id: toastId });
        } finally {
            setLoading(false);
        }
    };

    return (
        <aside className="w-72 border-r border-border bg-card flex flex-col shrink-0">
            <div className="p-4 border-b border-border">
                <form onSubmit={handleIngest} className="space-y-3">
                    <div className="relative">
                        <LinkIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                        <input
                            type="url"
                            placeholder="Paste PDF URL..."
                            className="w-full bg-background border border-border rounded-lg py-2 pl-9 pr-3 text-sm focus:outline-none focus:border-accent transition-colors"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={loading || !url.trim()}
                        className="w-full bg-accent hover:bg-accent/90 disabled:opacity-50 text-white rounded-lg py-2 text-sm font-medium transition-colors flex items-center justify-center gap-2"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                        Ingest Document
                    </button>
                </form>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <div className="flex items-center justify-between text-xs font-semibold text-muted uppercase tracking-wider">
                    <span>Documents</span>
                    <span className="bg-border px-1.5 py-0.5 rounded-full text-[10px]">{docs.length}</span>
                </div>

                {fetching ? (
                    <div className="flex justify-center py-8">
                        <Loader2 className="w-5 h-5 animate-spin text-muted" />
                    </div>
                ) : docs.length === 0 ? (
                    <div className="text-center py-8">
                        <p className="text-sm text-muted italic">No documents yet</p>
                    </div>
                ) : (
                    <div className="space-y-1">
                        {docs.map((doc, i) => (
                            <button
                                key={i}
                                onClick={() => onSelectDoc(doc)}
                                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-background transition-colors text-sm group"
                            >
                                <FileText className="w-4 h-4 text-accent group-hover:scale-110 transition-transform" />
                                <span className="truncate text-left flex-1" title={doc.name}>{doc.name}</span>
                            </button>
                        ))}
                    </div>
                )}
            </div>

            <div className="p-4 border-t border-border mt-auto bg-background/50">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                    <input
                        type="text"
                        placeholder="Search chats..."
                        className="w-full bg-background border border-border rounded-lg py-1.5 pl-9 pr-3 text-xs focus:outline-none focus:border-accent"
                    />
                </div>
            </div>
        </aside>
    );
}
