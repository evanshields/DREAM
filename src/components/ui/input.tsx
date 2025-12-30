import * as React from "react"
import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "h-9 w-full min-w-0 rounded-md border border-border bg-background-primary px-3 py-1 text-base text-secondary shadow-sm transition-colors outline-none placeholder:text-secondary-muted disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        "focus:border-accent focus:ring-2 focus:ring-accent/20",
        "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-secondary",
        className
      )}
      {...props}
    />
  )
}

export { Input }
