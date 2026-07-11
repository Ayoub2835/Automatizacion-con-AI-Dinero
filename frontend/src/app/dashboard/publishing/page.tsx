import { cookies } from "next/headers";

import { ConnectAccountForm } from "@/components/ConnectAccountForm";
import { Card } from "@/components/ui/Card";
import { SESSION_COOKIE_NAME } from "@/lib/config";
import { getDashboardSummary, getPublishingAccounts } from "@/lib/publishing";

const PLATFORM_LABELS: Record<string, string> = {
  kdp: "Amazon KDP",
  apple_books: "Apple Books",
  google_play_books: "Google Play Books",
  kobo: "Kobo",
};

const STATUS_LABELS: Record<string, string> = {
  draft: "Borrador",
  metadata_ready: "Metadatos listos",
  pending_review: "En revisión",
  approved: "Aprobada",
  submitted: "Enviada",
  live: "Publicada",
  rejected: "Rechazada",
  failed: "Error",
};

export default async function PublishingPage() {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value ?? "";
  const [accounts, summary] = await Promise.all([
    getPublishingAccounts(token),
    getDashboardSummary(token),
  ]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold">Publicación</h1>
        <p className="text-sm text-slate-600">
          Cuentas conectadas, estado de tus publicaciones y estadísticas de venta.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatTile label="Libros" value={summary.total_books} />
        <StatTile label="Publicaciones" value={summary.total_publications} />
        <StatTile label="Unidades vendidas" value={summary.total_units_sold} />
        <StatTile
          label="Ingresos"
          value={Object.entries(summary.revenue_by_currency)
            .map(([currency, amount]) => `${amount.toFixed(2)} ${currency}`)
            .join(" · ") || "0"}
        />
      </div>

      {Object.keys(summary.publications_by_status).length > 0 && (
        <Card className="w-full max-w-2xl">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">
            Publicaciones por estado
          </h2>
          <ul className="flex flex-wrap gap-3 text-sm text-slate-600">
            {Object.entries(summary.publications_by_status).map(([status, count]) => (
              <li key={status} className="rounded-full bg-slate-100 px-3 py-1">
                {STATUS_LABELS[status] ?? status}: {count}
              </li>
            ))}
          </ul>
        </Card>
      )}

      <Card className="w-full max-w-md">
        <h2 className="mb-4 text-sm font-semibold text-slate-700">Conectar cuenta</h2>
        <ConnectAccountForm />
        <p className="mt-3 text-xs text-slate-500">
          Ninguna de estas plataformas ofrece hoy autopublicación por API para autores
          independientes: la cuenta queda en modo asistido — BookAgent AI prepara los ficheros y
          metadatos, y tú completas la subida en el panel de la plataforma.
        </p>
      </Card>

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-2 font-medium">Plataforma</th>
              <th className="px-4 py-2 font-medium">Cuenta</th>
              <th className="px-4 py-2 font-medium">Estado</th>
            </tr>
          </thead>
          <tbody>
            {accounts.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-center text-slate-500">
                  Todavía no has conectado ninguna cuenta.
                </td>
              </tr>
            ) : (
              accounts.map((account) => (
                <tr key={account.id} className="border-b border-slate-100 last:border-0">
                  <td className="px-4 py-2">{PLATFORM_LABELS[account.platform] ?? account.platform}</td>
                  <td className="px-4 py-2">{account.display_name}</td>
                  <td className="px-4 py-2">{account.connection_status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatTile({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}
