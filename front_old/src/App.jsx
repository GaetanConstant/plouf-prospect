import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Search,
  MapPin,
  Users,
  Building2,
  Download,
  RefreshCw,
  Filter,
  ChevronRight,
  Loader2,
  FileSpreadsheet,
  Globe
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = 'http://localhost:8000';

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/results`);
      setResults(response.data);
    } catch (error) {
      console.error("Erreur lors de la récupération des résultats:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async (e) => {
    e.preventDefault();
    if (!searchTerm || !zipCode) return;

    setIsProcessing(true);
    try {
      await axios.post(`${API_URL}/process`, {
        keyword: searchTerm,
        zipcode: zipCode,
        max_fiches: 20
      });
      fetchResults();
    } catch (error) {
      console.error("Erreur lors du traitement:", error);
      alert("Une erreur est survenue lors du traitement.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans selection:bg-primary-500/30">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-primary-600/10 blur-[120px] rounded-full" />
        <div className="absolute top-[20%] -right-[5%] w-[30%] h-[30%] bg-indigo-600/10 blur-[100px] rounded-full" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <header className="mb-12 flex flex-col md:flex-row md:items-end md:justify-between gap-6">
          <div>
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm font-medium mb-4"
            >
              <Building2 className="w-4 h-4" />
              <span>Plouf Prospect Pro</span>
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400 tracking-tight"
            >
              Tableau de bord <span className="text-primary-500">Dirigeants</span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="mt-3 text-slate-400 max-w-xl text-lg"
            >
              Pilotez vos extractions, enrichissez vos données et prospectez plus efficacement.
            </motion.p>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={fetchResults}
              className="p-3 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-slate-500 transition-all text-slate-300 hover:text-white group"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin text-primary-400' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
            </button>
            <a
              href={`${API_URL}/results`}
              download
              className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-primary-600 hover:bg-primary-500 text-white font-semibold transition-all shadow-lg shadow-primary-600/20 active:scale-95"
            >
              <Download className="w-5 h-5" />
              <span>Exporter CSV</span>
            </a>
          </div>
        </header>

        {/* Search Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 p-6 rounded-3xl shadow-2xl mb-12"
        >
          <form onSubmit={handleProcess} className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-primary-400 transition-colors" />
              <input
                type="text"
                placeholder="Activité (ex: Plomberie)"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-900/50 border border-slate-700 rounded-2xl py-3.5 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all placeholder:text-slate-600"
              />
            </div>
            <div className="relative group">
              <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-primary-400 transition-colors" />
              <input
                type="text"
                placeholder="Code Postal (ex: 69400)"
                value={zipCode}
                onChange={(e) => setZipCode(e.target.value)}
                className="w-full bg-slate-900/50 border border-slate-700 rounded-2xl py-3.5 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all placeholder:text-slate-600"
              />
            </div>
            <div className="lg:col-span-1">
              <button
                type="submit"
                disabled={isProcessing}
                className={`w-full h-full rounded-2xl font-bold flex items-center justify-center space-x-2 transition-all ${isProcessing
                  ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white shadow-lg shadow-indigo-600/20 active:scale-[0.98]'
                  }`}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Scraping en cours...</span>
                  </>
                ) : (
                  <>
                    <Users className="w-5 h-5" />
                    <span>Lancer l'extraction</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </motion.div>

        {/* Results Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <StatCard title="Total Prospects" value={results.length} icon={<Building2 />} delay={0.4} />
          <StatCard title="Dirigeants Trouvés" value={results.filter(r => r.Dirigeants).length} icon={<Users />} delay={0.5} color="text-indigo-400" />
          <StatCard title="Localités" value={new Set(results.map(r => r.Adresse ? r.Adresse.split(' ').pop() : '')).size} icon={<MapPin />} delay={0.6} color="text-emerald-400" />
        </div>

        {/* Results Table */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl overflow-hidden shadow-2xl"
        >
          <div className="p-6 border-b border-slate-700/50 flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center space-x-2">
              <FileSpreadsheet className="w-5 h-5 text-primary-400" />
              <span>Liste des prospects enrichis</span>
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-900/30 text-slate-400 text-xs uppercase tracking-widest font-bold">
                  <th className="px-6 py-4">Entreprise / Enseigne</th>
                  <th className="px-6 py-4">Dirigeant(s)</th>
                  <th className="px-6 py-4">Ville</th>
                  <th className="px-6 py-4">Contact</th>
                  <th className="px-6 py-4"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/30">
                <AnimatePresence>
                  {results.length > 0 ? (
                    results.map((row, idx) => (
                      <motion.tr
                        key={idx}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="hover:bg-primary-500/5 transition-colors group"
                      >
                        <td className="px-6 py-5">
                          <div className="flex flex-col">
                            <span className="text-white font-semibold group-hover:text-primary-300 transition-colors uppercase tracking-tight">
                              {row.Nom || 'N/A'}
                            </span>
                            <span className="text-xs text-slate-500 font-mono mt-0.5">SIRET: {row.SIRET || 'Inconnu'}</span>
                          </div>
                        </td>
                        <td className="px-6 py-5">
                          <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-300">
                              {row.Dirigeants ? row.Dirigeants.charAt(0) : '?'}
                            </div>
                            <span className={`${row.Dirigeants ? 'text-indigo-300' : 'text-slate-600 italic'}`}>
                              {row.Dirigeants || 'Non trouvé'}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-5">
                          <div className="flex flex-col">
                            <span className="text-slate-300 truncate max-w-[200px]">{row.Adresse || 'N/A'}</span>
                          </div>
                        </td>
                        <td className="px-6 py-5 text-slate-400">
                          {row.Téléphone || row['Téléphone trouvé sur site'] ? (
                            <span className="bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded text-sm font-medium border border-emerald-500/20">
                              {row.Téléphone || row['Téléphone trouvé sur site']}
                            </span>
                          ) : (
                            <span className="text-slate-600">Aucun numéro</span>
                          )}
                        </td>
                        <td className="px-6 py-5 text-right flex items-center justify-end space-x-3">
                          {row['Site web'] && (
                            <a
                              href={row['Site web'].startsWith('http') ? row['Site web'] : `https://${row['Site web']}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-slate-500 hover:text-emerald-400 transition-colors"
                              title="Visiter le site web"
                            >
                              <Globe className="w-5 h-5" />
                            </a>
                          )}
                          {row['Lien Pappers'] && (
                            <a
                              href={row['Lien Pappers']}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-slate-500 hover:text-primary-400 transition-colors"
                              title="Voir sur Pappers"
                            >
                              <ChevronRight className="w-5 h-5" />
                            </a>
                          )}
                        </td>
                      </motion.tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="px-6 py-20 text-center">
                        {loading ? (
                          <div className="flex flex-col items-center">
                            <Loader2 className="w-10 h-10 animate-spin text-primary-500 mb-4" />
                            <p className="text-slate-400">Chargement des prospects...</p>
                          </div>
                        ) : (
                          <div className="flex flex-col items-center">
                            <Building2 className="w-12 h-12 text-slate-700 mb-4" />
                            <p className="text-slate-500">Aucun résultat trouvé. Lancez une recherche pour commencer.</p>
                          </div>
                        )}
                      </td>
                    </tr>
                  )}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Footer */}
        <footer className="mt-20 text-center text-slate-600 text-sm">
          <p>&copy; 2026 Plouf Prospect - Intelligence de Prospection v1.0.0</p>
        </footer>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, delay, color = "text-primary-400" }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay }}
      className="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 p-6 rounded-3xl hover:border-slate-600/50 transition-all flex items-center space-x-6 group"
    >
      <div className={`p-4 rounded-2xl bg-slate-900 group-hover:scale-110 transition-transform ${color}`}>
        {React.cloneElement(icon, { className: "w-6 h-6" })}
      </div>
      <div>
        <h3 className="text-slate-400 text-sm font-medium">{title}</h3>
        <p className="text-3xl font-bold text-white mt-1">{value}</p>
      </div>
    </motion.div>
  );
}

export default App;
