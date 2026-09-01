"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/" },
  { label: "Courses", href: "/courses" },
  { label: "Lessons", href: "/lessons" },
  { label: "Assets", href: "/assets" },
  { label: "Settings", href: "/settings" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-60 flex-col border-r border-gray-200 bg-gray-900">
      <div className="px-5 py-6">
        <h1 className="text-lg font-semibold text-white">Content Factory</h1>
        <p className="text-xs text-gray-400">LA App Platform</p>
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? "bg-gray-700 text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-gray-700 px-5 py-3">
        <p className="text-xs text-gray-500">v0.1.0</p>
      </div>
    </aside>
  );
}
