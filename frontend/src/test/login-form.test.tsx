import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

import { LoginForm } from "@/components/LoginForm";

describe("LoginForm", () => {
  it("renderiza los campos de email y contraseña", () => {
    render(<LoginForm />);

    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Contraseña")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /entrar/i })).toBeInTheDocument();
  });

  it("enlaza a la página de registro", () => {
    render(<LoginForm />);

    expect(screen.getByRole("link", { name: /regístrate/i })).toHaveAttribute("href", "/register");
  });
});
