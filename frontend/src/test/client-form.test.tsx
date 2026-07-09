import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

import { ClientForm } from "@/components/ClientForm";

describe("ClientForm", () => {
  it("renderiza los campos de nombre, email y teléfono", () => {
    render(<ClientForm />);

    expect(screen.getByLabelText("Nombre")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Teléfono (opcional)")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /añadir cliente/i })).toBeInTheDocument();
  });

  it("el teléfono no es obligatorio", () => {
    render(<ClientForm />);

    expect(screen.getByLabelText("Teléfono (opcional)")).not.toBeRequired();
    expect(screen.getByLabelText("Nombre")).toBeRequired();
    expect(screen.getByLabelText("Email")).toBeRequired();
  });
});
