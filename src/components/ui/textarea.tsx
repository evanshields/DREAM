import * as React from "react"
import { cn } from "@/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "flex min-h-16 w-full rounded-md border border-border bg-background-primary px-3 py-2 text-base text-secondary shadow-sm transition-colors outline-none placeholder:text-secondary-muted disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        "focus:border-accent focus:ring-2 focus:ring-accent/20",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }


