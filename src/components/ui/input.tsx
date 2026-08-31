import { cn } from "@/lib/utils";
import type { InputHTMLAttributes } from "react";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-11 w-full rounded-full border border-white/12 bg-white/5 px-4 text-sm text-paper outline-none placeholder:text-paper/40 focus:border-lime/60",
        className,
      )}
      {...props}
    />
  );
}
