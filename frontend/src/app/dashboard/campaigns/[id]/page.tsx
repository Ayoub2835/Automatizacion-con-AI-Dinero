import { cookies } from "next/headers";
import { notFound } from "next/navigation";

import { SendCampaignForm } from "@/components/SendCampaignForm";
import { Card } from "@/components/ui/Card";
import { BackendError } from "@/lib/backend-client";
import { getCampaign } from "@/lib/campaigns";
import { getClients } from "@/lib/clients";
import { SESSION_COOKIE_NAME } from "@/lib/config";

export default async function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value ?? "";

  const [campaign, clients] = await Promise.all([
    getCampaign(token, id).catch((error: unknown) => {
      if (error instanceof BackendError && error.status === 404) {
        notFound();
      }
      throw error;
    }),
    getClients(token),
  ]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold">{campaign.name}</h1>
        <p className="text-sm text-slate-600">
          Documentos solicitados: {campaign.document_types.map((t) => t.name).join(", ")}
        </p>
      </div>

      <Card className="w-full max-w-lg">
        <h2 className="mb-4 text-sm font-semibold text-slate-700">Enviar a clientes</h2>
        <SendCampaignForm campaignId={campaign.id} clients={clients} />
      </Card>
    </div>
  );
}
