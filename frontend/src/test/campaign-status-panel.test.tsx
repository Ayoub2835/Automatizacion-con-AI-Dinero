import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

import { CampaignStatusPanel } from "@/components/CampaignStatusPanel";
import type { CampaignStatusResponse } from "@/lib/types";

const status: CampaignStatusResponse = {
  campaign_id: "campaign-1",
  campaign_name: "Campaña Renta",
  clients: [
    {
      campaign_client_id: "cc-1",
      client_id: "client-1",
      client_name: "Cliente Completo",
      client_email: "completo@example.com",
      status: "complete",
      document_types: [{ name: "DNI", satisfied: true }],
      documents: [
        {
          id: "doc-1",
          original_filename: "dni.pdf",
          document_type_name: "DNI",
          status: "classified",
          uploaded_at: "2026-01-01T00:00:00Z",
        },
      ],
    },
    {
      campaign_client_id: "cc-2",
      client_id: "client-2",
      client_name: "Cliente Pendiente",
      client_email: "pendiente@example.com",
      status: "pending",
      document_types: [{ name: "DNI", satisfied: false }],
      documents: [],
    },
  ],
};

describe("CampaignStatusPanel", () => {
  it("muestra el resumen de completos y pendientes", () => {
    render(<CampaignStatusPanel status={status} />);

    expect(screen.getByText("Completos:")).toBeInTheDocument();
    expect(screen.getByText("Pendientes:")).toBeInTheDocument();
    expect(screen.getByText("Cliente Completo")).toBeInTheDocument();
    expect(screen.getByText("Cliente Pendiente")).toBeInTheDocument();
  });

  it("muestra el botón de reenviar recordatorio", () => {
    render(<CampaignStatusPanel status={status} />);

    expect(
      screen.getByRole("button", { name: /reenviar recordatorio a pendientes/i }),
    ).toBeInTheDocument();
  });

  it("muestra un aviso cuando no se ha enviado a nadie", () => {
    render(<CampaignStatusPanel status={{ ...status, clients: [] }} />);

    expect(screen.getByText(/todavía no has enviado esta campaña/i)).toBeInTheDocument();
  });
});
