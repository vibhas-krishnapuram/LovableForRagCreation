import * as React from "react"
// Oops, I didn't install class-variance-authority or radix-ui/react-slot. I should stick to simple props or install them. 
// The plan didn't mention cva or radix. I should stick to a simpler implementation using clsx/tailwind-merge without cva for now unless I install it. 
// Actually, for a "startup" feel, cva is very standard. I'll just use a simpler implementation for now to avoid extra installs unless I find I need them.
// Wait, I can just install class-variance-authority and @radix-ui/react-slot, they are standard. 
// But strictly following the plan... the plan didn't explicitly say "install cva".
// I will implement a simpler version without CVA first to be safe and avoid "installing unapproved dependencies" although I could have added them.
// Actually, I can just use a switch or map for variants.

import { cn } from "../../lib/utils"

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"
    size?: "default" | "sm" | "lg" | "icon"
    asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "default", size = "default", asChild = false, ...props }, ref) => {
        // Simplified variant handling without cva
        const baseStyles = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"

        const variants = {
            default: "bg-primary text-primary-foreground hover:bg-primary/90",
            destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
            outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
            secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
            ghost: "hover:bg-accent hover:text-accent-foreground",
            link: "text-primary underline-offset-4 hover:underline",
        }

        const sizes = {
            default: "h-10 px-4 py-2",
            sm: "h-9 rounded-md px-3",
            lg: "h-11 rounded-md px-8",
            icon: "h-10 w-10",
        }

        const Comp = "button" // wrapper for asChild not implemented to avoid radix dependency for now

        return (
            <Comp
                className={cn(baseStyles, variants[variant], sizes[size], className)}
                ref={ref}
                {...props}
            />
        )
    }
)
Button.displayName = "Button"

export { Button }
