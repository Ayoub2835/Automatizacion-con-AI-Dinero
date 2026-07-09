import { cookies } from "next/headers";

import { ClientForm } from "@/components/ClientForm";
import { Card } from "@/components/ui/Card";
import { getClients } from "@/lib/clients";
import { SESSION_COOKIE_NAME } from "@/lib/config";

export default async function ClientsPage() {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value ?? "";
  const clients = await getClients(token);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold">Clientes</h1>
        <p className="text-sm text-slate-600">
          Los clientes de tu gestoría. Añádelos aquí antes de enviarles una campaña de
          documentación.
        </p>
      </div>

      <Card className="w-full max-w-md">
        <h2 className="mb-4 text-sm font-semibold text-slate-700">Añadir cliente</h2>
        <ClientForm />
      </Card>

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-2 font-medium">Nombre</th>
              <th className="px-4 py-2 font-medium">Email</th>
              <th className="px-4 py-2 font-medium">Teléfono</th>
            </tr>
          </thead>
          <tbody>
            {clients.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-center text-slate-500">
                  Todavía no has añadido ningún cliente.
                </td>
              </tr>
            ) : (
              clients.map((client) => (
                <tr key={client.id} className="border-b border-slate-100 last:border-0">
                  <td className="px-4 py-2">{client.name}</td>
                  <td className="px-4 py-2">{client.email}</td>
                  <td className="px-4 py-2">{client.phone ?? "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
