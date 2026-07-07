import { RegisterForm } from "@/components/RegisterForm";
import { Card } from "@/components/ui/Card";

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <Card>
        <h1 className="mb-6 text-center text-xl font-semibold">Crear cuenta de gestoría</h1>
        <RegisterForm />
      </Card>
    </main>
  );
}
