import { createRoot } from "react-dom/client";
import Atlas from "../app/page";
import "../app/globals.css";

const atlas = document.getElementById("atlas");
if (!atlas) throw new Error("Falta el contenedor del visor.");

createRoot(atlas).render(<Atlas />);
