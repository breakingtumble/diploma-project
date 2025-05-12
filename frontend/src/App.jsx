import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Product from "./pages/Product";
import Register from "./pages/Register";
import Login from "./pages/Login";
import TopBar from "./components/TopBar";
import NotFound from "./pages/NotFound";
import Subscriptions from "./pages/Subscriptions";
import MarketplaceConfigs from './pages/MarketplaceConfigs';
import EditMarketplaceConfig from './pages/EditMarketplaceConfig';
import NewMarketplaceConfig from './pages/NewMarketplaceConfig';

function Layout({ children }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw' }}>
      <TopBar />
      <main style={{ flex: 1, overflow: 'auto', padding: '1rem' }}>
        {children}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/product/:id" element={<Product />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/subscriptions" element={<Subscriptions />} />
          <Route path="/marketplace-configs" element={<MarketplaceConfigs />} />
          <Route path="/marketplace-configs/new" element={<NewMarketplaceConfig />} />
          <Route path="/marketplace-configs/:configName" element={<EditMarketplaceConfig />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
