import { type ReactNode } from "react";

export function Card({
  children,
  className = "w-full max-w-sm",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-lg border border-slate-200 bg-white p-8 shadow-sm ${className}`}>
      {children}
    </div>
  );
}
