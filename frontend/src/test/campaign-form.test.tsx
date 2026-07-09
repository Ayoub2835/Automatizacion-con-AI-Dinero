import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

import { CampaignForm } from "@/components/CampaignForm";

describe("CampaignForm", () => {
  it("renderiza el nombre y los tipos de documento", () => {
    render(<CampaignForm />);

    expect(screen.getByLabelText("Nombre de la campaña")).toBeInTheDocument();
    expect(
      screen.getByLabelText("Documentos a solicitar (separados por comas)"),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /crear campaña/i })).toBeInTheDocument();
  });
});
