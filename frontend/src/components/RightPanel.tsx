import { useState, useEffect, useRef, useCallback } from "react";
import Editor, { type Monaco } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import { Play, Terminal as TerminalIcon, XCircle, CheckCircle2, Loader2, Trash2 } from "lucide-react";
import { api } from "../api";
import { toast } from "sonner";

interface RightPanelProps {
    code: string;
}

export function RightPanel({ code }: RightPanelProps) {
    const [editorCode, setEditorCode] = useState("");
    const [output, setOutput] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [running, setRunning] = useState(false);
    const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
    const monacoRef = useRef<Monaco | null>(null);

    useEffect(() => {
        if (code) {
            setEditorCode(code);
        }
    }, [code]);

    const handleRun = useCallback(async () => {
        const currentCode = editorRef.current?.getValue() || editorCode;
        if (!currentCode.trim() || running) return;

        setRunning(true);
        setOutput(null);
        setError(null);
        const toastId = toast.loading("Executing code in sandbox...");

        try {
            const result = await api.executeCode(currentCode);
            if (result.error) {
                setError(result.error);
                toast.error("Execution failed", { id: toastId });
            } else {
                setOutput(result.output || "No output");
                toast.success("Execution successful", { id: toastId });
            }
        } catch (err: any) {
            setError(err.message || "Unknown error");
            toast.error("Execution error", { id: toastId });
        } finally {
            setRunning(false);
        }
    }, [editorCode, running]);

    const handleEditorMount = (ed: editor.IStandaloneCodeEditor, monaco: Monaco) => {
        editorRef.current = ed;
        monacoRef.current = monaco;
        ed.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
            handleRun();
        });
    };

    return (
        <div className="w-[450px] border-l border-border bg-card flex flex-col shrink-0">
            {/* Toolbar */}
            <div className="h-12 border-b border-border flex items-center justify-between px-4 bg-background/30">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted">
                    <TerminalIcon className="w-3.5 h-3.5" />
                    <span>Sandbox Editor</span>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setEditorCode("")}
                        className="p-1.5 hover:bg-border rounded transition-colors text-muted hover:text-foreground"
                        title="Clear Editor"
                    >
                        <Trash2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                        onClick={handleRun}
                        disabled={running || !editorCode.trim()}
                        className="flex items-center gap-1.5 bg-accent hover:bg-accent/90 px-3 py-1.5 rounded-md text-xs font-bold transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:scale-100"
                    >
                        {running ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3 fill-current" />}
                        RUN
                        <span className="opacity-60 font-normal">⌘+↵</span>
                    </button>
                </div>
            </div>

            {/* Editor */}
            <div className="flex-1 min-h-0 bg-background">
                <Editor
                    height="100%"
                    defaultLanguage="python"
                    theme="vs-dark"
                    value={editorCode}
                    onChange={(v) => setEditorCode(v || "")}
                    options={{
                        minimap: { enabled: false },
                        fontSize: 13,
                        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                        scrollBeyondLastLine: false,
                        padding: { top: 16 },
                        lineNumbers: "on",
                        bracketPairColorization: { enabled: true },
                    }}
                    onMount={handleEditorMount}
                />
            </div>

            {/* Terminal */}
            <div className="h-64 border-t border-border flex flex-col bg-background/50">
                <div className="h-10 border-b border-border flex items-center justify-between px-4 shrink-0 bg-background/30">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted">Terminal Output</span>
                    {(output || error) && (
                        <button
                            onClick={() => { setOutput(null); setError(null); }}
                            className="text-[10px] text-muted hover:text-foreground underline underline-offset-2"
                        >
                            Clear
                        </button>
                    )}
                </div>

                <div className="flex-1 overflow-y-auto p-4 font-mono text-xs leading-relaxed">
                    {!output && !error && !running && (
                        <div className="text-muted italic h-full flex items-center justify-center opacity-50">
                            Terminal ready...
                        </div>
                    )}

                    {running && (
                        <div className="flex items-center gap-3 text-accent animate-pulse">
                            <span className="w-1.5 h-1.5 bg-accent rounded-full" />
                            Executing script...
                        </div>
                    )}

                    {error && (
                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-red-400 font-bold">
                                <XCircle className="w-4 h-4" />
                                <span>Runtime Error</span>
                            </div>
                            <pre className="bg-red-500/10 border border-red-500/20 p-3 rounded text-red-300 whitespace-pre-wrap">{error}</pre>
                        </div>
                    )}

                    {output && (
                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-green-400 font-bold">
                                <CheckCircle2 className="w-4 h-4" />
                                <span>Success</span>
                            </div>
                            <pre className="bg-green-500/10 border border-green-500/20 p-3 rounded text-green-300 whitespace-pre-wrap">{output}</pre>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
