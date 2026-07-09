import { notFound } from "next/navigation";

import { UploadDocumentForm } from "@/components/UploadDocumentForm";
import { Card } from "@/components/ui/Card";
import { BackendError } from "@/lib/backend-client";
import { getPublicCampaignStatus } from "@/lib/public";

export default async function PublicUploadPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;

  const status = await getPublicCampaignStatus(token).catch((error: unknown) => {
    if (error instanceof BackendError && error.status === 404) {
      notFound();
    }
    throw error;
  });

  const isComplete = status.client_status === "complete";

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <Card className="w-full max-w-lg">
        <h1 className="mb-1 text-lg font-semibold">{status.campaign_name}</h1>
        <p className="mb-4 text-sm text-slate-600">
          Sube aquí la documentación que te ha solicitado tu gestoría.
        </p>

        <ul className="mb-6 flex flex-col gap-1 text-sm">
          {status.document_types.map((docType) => (
            <li key={docType.name} className="flex items-center gap-2">
              <span aria-hidden>{docType.satisfied ? "✅" : "⬜"}</span>
              {docType.name}
            </li>
          ))}
        </ul>

        {isComplete ? (
          <p className="rounded-md bg-green-50 p-3 text-sm text-green-800">
            ¡Gracias! Ya has enviado toda la documentación solicitada.
          </p>
        ) : (
          <UploadDocumentForm token={token} />
        )}

        {status.documents.length > 0 && (
          <div className="mt-6 border-t border-slate-200 pt-4">
            <h2 className="mb-2 text-sm font-semibold text-slate-700">Documentos recibidos</h2>
            <ul className="flex flex-col gap-1 text-sm text-slate-600">
              {status.documents.map((document) => (
                <li key={document.id}>
                  {document.original_filename} —{" "}
                  {document.document_type_name ?? "sin clasificar todavía"}
                </li>
              ))}
            </ul>
          </div>
        )}
      </Card>
    </div>
  );
}
