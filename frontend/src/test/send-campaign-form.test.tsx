import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

import { SendCampaignForm } from "@/components/SendCampaignForm";
import type { Client } from "@/lib/types";

const clients: Client[] = [
  {
    id: "client-1",
    organization_id: "org-1",
    name: "Cliente Uno",
    email: "uno@example.com",
    phone: null,
    created_at: "2026-01-01T00:00:00Z",
  },
];

describe("SendCampaignForm", () => {
  it("renderiza un checkbox por cliente y el botón de enviar", () => {
    render(<SendCampaignForm campaignId="campaign-1" clients={clients} />);

    expect(screen.getByLabelText("Cliente Uno (uno@example.com)")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /enviar campaña a los seleccionados/i }),
    ).toBeInTheDocument();
  });

  it("muestra un aviso cuando no hay clientes", () => {
    render(<SendCampaignForm campaignId="campaign-1" clients={[]} />);

    expect(screen.getByText(/todavía no tienes clientes/i)).toBeInTheDocument();
  });
});
