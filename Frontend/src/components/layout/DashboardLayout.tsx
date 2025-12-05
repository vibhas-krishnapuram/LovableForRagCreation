import { Sidebar } from "./Sidebar";
import { Menu } from "lucide-react";
import { useState } from "react";
import { Button } from "../ui/Button";

interface DashboardLayoutProps {
    children: React.ReactNode;
}

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="min-h-screen bg-background text-foreground flex">
            {/* Desktop Sidebar */}
            <div className="hidden md:block">
                <Sidebar />
            </div>

            {/* Mobile Sidebar Overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 md:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Mobile Sidebar */}
            <div className={
                `fixed inset-y-0 left-0 z-50 w-64 bg-background border-r transform transition-transform duration-200 ease-in-out md:hidden ${sidebarOpen ? "translate-x-0" : "-translate-x-full"
                }`
            }>
                <Sidebar />
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-h-screen transition-all duration-300">
                <header className="h-16 border-b flex items-center px-4 md:hidden">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setSidebarOpen(true)}
                    >
                        <Menu className="h-6 w-6" />
                    </Button>
                    <span className="ml-4 font-bold">RAG Creator</span>
                </header>

                <main className="flex-1 p-6 md:p-8 overflow-y-auto w-full max-w-7xl mx-auto">
                    {children}
                </main>
            </div>
        </div>
    );
};
