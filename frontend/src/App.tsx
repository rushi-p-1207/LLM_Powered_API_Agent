import { useState } from "react";
import { TopNav } from "./components/TopNav";
import { LeftSidebar } from "./components/LeftSidebar";
import { ChatPanel } from "./components/ChatPanel";
import { RightPanel } from "./components/RightPanel";
import { Toaster } from "sonner";

function App() {
  const [selectedCode, setSelectedCode] = useState("");

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden text-foreground selection:bg-accent/30">
      <TopNav />

      <main className="flex-1 flex overflow-hidden">
        <LeftSidebar onSelectDoc={(doc) => console.log("Selected doc:", doc)} />

        <ChatPanel onCodeDetected={setSelectedCode} />

        <RightPanel code={selectedCode} />
      </main>

      <Toaster
        theme="dark"
        richColors
        position="top-right"
        toastOptions={{
          style: {
            background: "#1A1A2E",
            border: "1px solid #2D2D44",
            color: "#FFFFFE",
          },
        }}
      />
    </div>
  );
}

export default App;
