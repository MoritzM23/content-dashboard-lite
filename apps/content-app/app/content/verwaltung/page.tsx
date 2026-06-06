import { redirect } from 'next/navigation';

// Verwaltung-Tab wurde durch das Settings-Sheet in den ContentTabs ersetzt
// (Zahnrad rechts neben den Tabs). Direkt-Aufruf des alten /verwaltung-Pfades
// landet jetzt auf Mein-Account.
export default function VerwaltungPage() {
  redirect('/content/mein-account');
}
