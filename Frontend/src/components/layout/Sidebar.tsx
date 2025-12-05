import { Home, Plus, LogOut } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "../../lib/utils";
import { useAuth } from "../../contexts/AuthContext";

export const Sidebar = () => {
    const { pathname } = useLocation();
    const { logout } = useAuth();

    const links = [
        { href: "/dashboard", label: "Dashboard", icon: Home },
        { href: "/create", label: "Create RAG", icon: Plus },
    ];

    return (
        <div className="flex flex-col h-full border-r bg-background w-64">
            <div className="p-6">
                <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                    RAG Creator
                </h1>
            </div>

            <div className="flex-1 px-4 py-2 space-y-2">
                {links.map((link) => {
                    const Icon = link.icon;
                    const isActive = pathname === link.href;

                    return (
                        <Link
                            key={link.href}
                            to={link.href}
                            className={cn(
                                "flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200",
                                isActive
                                    ? "bg-primary text-primary-foreground shadow-sm"
                                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                            )}
                        >
                            <Icon size={20} />
                            <span>{link.label}</span>
                        </Link>
                    );
                })}
            </div>

            <div className="p-4 border-t">
                <button
                    onClick={logout}
                    className="flex items-center gap-3 px-3 py-2 w-full text-muted-foreground hover:bg-destructive/10 hover:text-destructive rounded-md transition-colors"
                >
                    <LogOut size={20} />
                    <span>Logout</span>
                </button>
            </div>
        </div>
    );
};
