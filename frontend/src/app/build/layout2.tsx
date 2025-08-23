"use client";
import { TopNav } from "@/components/layout/TopNav";
import { Footer } from "@/app/page";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen w-full text-white overflow-x-hidden">
      <TopNav onDocs={() => alert("Docs coming soon")} />
    </div>
  );
}
