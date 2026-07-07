import { redirect } from "next/navigation";

// El middleware ya protege las rutas; esta redirección cubre la raíz "/".
export default function RootPage() {
  redirect("/dashboard");
}
