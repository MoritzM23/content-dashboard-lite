import { redirect } from 'next/navigation';

// TikTok-Tab wurde in /content/planung als 4. Plattform-Pill integriert.
// Direkt-Aufruf des alten /tiktok-Pfades landet auf der Planung mit Filter.
export default function TiktokPage() {
  redirect('/content/planung?platform=tiktok');
}
