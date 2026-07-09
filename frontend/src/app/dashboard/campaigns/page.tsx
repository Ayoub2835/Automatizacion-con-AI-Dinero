import Link from "next/link";
import { cookies } from "next/headers";

import { CampaignForm } from "@/components/CampaignForm";
import { Card } from "@/components/ui/Card";
import { getCampaigns } from "@/lib/campaigns";
import { SESSION_COOKIE_NAME } from "@/lib/config";

export default async function CampaignsPage() {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value ?? "";
  const campaigns = await getCampaigns(token);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold">Campañas</h1>
        <p className="text-sm text-slate-600">
          Crea una campaña con los documentos que necesitas y envíasela a tus clientes.
        </p>
      </div>

      <Card className="w-full max-w-md">
        <h2 className="mb-4 text-sm font-semibold text-slate-700">Nueva campaña</h2>
        <CampaignForm />
      </Card>

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-2 font-medium">Nombre</th>
              <th className="px-4 py-2 font-medium">Documentos solicitados</th>
              <th className="px-4 py-2 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {campaigns.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-center text-slate-500">
                  Todavía no has creado ninguna campaña.
                </td>
              </tr>
            ) : (
              campaigns.map((campaign) => (
                <tr key={campaign.id} className="border-b border-slate-100 last:border-0">
                  <td className="px-4 py-2">{campaign.name}</td>
                  <td className="px-4 py-2">
                    {campaign.document_types.map((t) => t.name).join(", ")}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <Link
                      href={`/dashboard/campaigns/${campaign.id}`}
                      className="font-medium text-slate-900 underline"
                    >
                      Ver / enviar
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
