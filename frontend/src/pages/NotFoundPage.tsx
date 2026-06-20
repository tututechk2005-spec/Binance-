import { Link } from "react-router-dom";
import { Home, AlertTriangle } from "lucide-react";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-[#0b0e11] flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 bg-[#1e2026] rounded-2xl flex items-center justify-center mx-auto mb-6 border border-[#2b2f36]">
          <AlertTriangle size={36} className="text-gold-DEFAULT" />
        </div>
        <h1 className="text-6xl font-bold text-gold-DEFAULT mb-3">404</h1>
        <h2 className="text-2xl font-semibold text-white mb-2">Page Not Found</h2>
        <p className="text-gray-400 mb-8">The page you're looking for doesn't exist or has been moved.</p>
        <Link to="/dashboard" className="btn-primary inline-flex items-center gap-2 px-6 py-3">
          <Home size={16} /> Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
