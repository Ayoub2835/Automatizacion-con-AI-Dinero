"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export function SalesRecordForm({ publicationId }: { publicationId: string }) {
  const router = useRouter();
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [unitsSold, setUnitsSold] = useState(0);
  const [revenueAmount, setRevenueAmount] = useState(0);
  const [currency, setCurrency] = useState("EUR");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const response = await fetch(`/api/publications/${publicationId}/sales`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        period_start: new Date(periodStart).toISOString(),
        period_end: new Date(periodEnd).toISOString(),
        units_sold: unitsSold,
        revenue_amount: revenueAmount,
        currency,
      }),
    });
    setIsSubmitting(false);

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
      setError(body.detail ?? "No se pudo registrar la venta");
      return;
    }

    setUnitsSold(0);
    setRevenueAmount(0);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="grid grid-cols-2 gap-3">
        <Input
          id="period_start"
          label="Desde"
          type="date"
          required
          value={periodStart}
          onChange={(e) => setPeriodStart(e.target.value)}
        />
        <Input
          id="period_end"
          label="Hasta"
          type="date"
          required
          value={periodEnd}
          onChange={(e) => setPeriodEnd(e.target.value)}
        />
      </div>
      <div className="grid grid-cols-3 gap-3">
        <Input
          id="units_sold"
          label="Unidades vendidas"
          type="number"
          min={0}
          required
          value={unitsSold}
          onChange={(e) => setUnitsSold(Number(e.target.value))}
        />
        <Input
          id="revenue_amount"
          label="Ingresos"
          type="number"
          min={0}
          step="0.01"
          required
          value={revenueAmount}
          onChange={(e) => setRevenueAmount(Number(e.target.value))}
        />
        <Input
          id="currency"
          label="Divisa"
          type="text"
          maxLength={3}
          required
          value={currency}
          onChange={(e) => setCurrency(e.target.value.toUpperCase())}
        />
      </div>
      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
      <Button type="submit" disabled={isSubmitting} className="w-fit">
        {isSubmitting ? "Guardando..." : "Registrar venta"}
      </Button>
    </form>
  );
}
