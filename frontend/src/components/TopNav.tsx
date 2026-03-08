import { Bell, User } from "lucide-react";

export function TopNav() {
    return (
        <nav className="h-14 border-b border-border bg-card flex items-center justify-between px-6 shrink-0">
            <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center font-bold text-lg">S</div>
                <h1 className="font-bold text-lg tracking-tight">LLM-Powered SmartAPI Agent</h1>
            </div>

            <div className="flex items-center gap-4">
                <button className="p-2 hover:bg-background rounded-full transition-colors relative">
                    <Bell className="w-5 h-5 text-muted hover:text-foreground" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-accent rounded-full border-2 border-card"></span>
                </button>
                <div className="flex items-center gap-3 pl-2 border-l border-border">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium">Hiren</p>
                        <p className="text-xs text-muted">Developer</p>
                    </div>
                    <div className="w-9 h-9 rounded-full bg-border flex items-center justify-center border border-accent/20">
                        <User className="w-5 h-5" />
                    </div>
                </div>
            </div>
        </nav>
    );
}
