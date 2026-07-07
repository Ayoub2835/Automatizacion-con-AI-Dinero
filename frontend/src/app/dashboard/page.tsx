import { Card } from "@/components/ui/Card";

export default function DashboardPage() {
  return (
    <Card>
      <h1 className="mb-2 text-lg font-semibold">Bienvenido a GestorIA</h1>
      <p className="text-sm text-slate-600">
        Esto es una base de panel intencionalmente vacía: todavía estamos validando con clientes
        reales qué funcionalidad construir aquí. Ver{" "}
        <code className="rounded bg-slate-100 px-1 py-0.5">ROADMAP.md</code> en la raíz del
        repositorio.
      </p>
    </Card>
  );
}
