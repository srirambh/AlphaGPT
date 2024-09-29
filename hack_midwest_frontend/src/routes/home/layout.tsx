import Sidebar from "@/sidebar";
import { Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="bg-background h-screen w-full flex flex-row">
      <Sidebar />
      <Outlet />
    </div>
  );
}
