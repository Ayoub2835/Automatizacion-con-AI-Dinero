import { LoginForm } from "@/components/LoginForm";
import { Card } from "@/components/ui/Card";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <Card>
        <h1 className="mb-6 text-center text-xl font-semibold">Iniciar sesión</h1>
        <LoginForm />
      </Card>
    </main>
  );
}
