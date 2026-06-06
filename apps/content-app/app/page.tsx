import { redirect } from 'next/navigation';

// Lite-Modul: nur Content. Root-Pfad geht direkt in den Content-Bereich.
export default function RootPage() {
  redirect('/content/mein-account');
}
