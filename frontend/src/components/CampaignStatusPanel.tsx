import { RemindButton } from "@/components/RemindButton";
import type { CampaignStatusResponse } from "@/lib/types";

export function CampaignStatusPanel({ status }: { status: CampaignStatusResponse }) {
  const completeCount = status.clients.filter((c) => c.status === "complete").length;
  const pendingCount = status.clients.length - completeCount;

  if (status.clients.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        Todavía no has enviado esta campaña a ningún cliente.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex gap-6 text-sm">
          <span>
            Completos: <strong>{completeCount}</strong>
          </span>
          <span>
            Pendientes: <strong>{pendingCount}</strong>
          </span>
        </div>
        <RemindButton campaignId={status.campaign_id} />
      </div>

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-2 font-medium">Cliente</th>
              <th className="px-4 py-2 font-medium">Estado</th>
              <th className="px-4 py-2 font-medium">Documentos faltantes</th>
              <th className="px-4 py-2 font-medium">Documentos recibidos</th>
            </tr>
          </thead>
          <tbody>
            {status.clients.map((client) => {
              const missing = client.document_types.filter((t) => !t.satisfied);
              return (
                <tr key={client.campaign_client_id} className="border-b border-slate-100 last:border-0">
                  <td className="px-4 py-2">
                    {client.client_name}
                    <div className="text-xs text-slate-500">{client.client_email}</div>
                  </td>
                  <td className="px-4 py-2">
                    <span
                      className={
                        client.status === "complete"
                          ? "rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800"
                          : "rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800"
                      }
                    >
                      {client.status === "complete" ? "Completo" : "Pendiente"}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    {missing.length === 0 ? "—" : missing.map((t) => t.name).join(", ")}
                  </td>
                  <td className="px-4 py-2">
                    {client.documents.length === 0
                      ? "—"
                      : client.documents
                          .map((d) => d.document_type_name ?? `${d.original_filename} (sin clasificar)`)
                          .join(", ")}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
