import type { Metadata } from 'next';
import './globals.css';
export const metadata:Metadata={title:'Mediterranean Multiproxy Atlas',description:'Registros marinos y continentales, mapas de proxies y series temporales con fuentes verificables.',icons:{icon:'/favicon.svg'}};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="es"><head><meta name="viewport" content="width=device-width, initial-scale=1"/><link rel="stylesheet" href="/vendor/leaflet/leaflet.css"/></head><body>{children}</body></html>;}
