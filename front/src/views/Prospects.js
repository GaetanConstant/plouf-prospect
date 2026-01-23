import React, { useState, useEffect } from "react";
import axios from "axios";
import {
    Card,
    CardHeader,
    CardBody,
    CardTitle,
    Table,
    Row,
    Col,
    Input,
    Button,
    FormGroup,
    Form,
    Spinner,
} from "reactstrap";

const API_URL = "http://localhost:8000";

function Prospects() {
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const [zipCode, setZipCode] = useState("");
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
                max_fiches: 20,
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
        <>
            <div className="content">
                <Row>
                    <Col md="12">
                        <Card>
                            <CardHeader>
                                <CardTitle tag="h4">Recherche de Prospects</CardTitle>
                                <p className="card-category">
                                    Entrez une activité et un code postal pour lancer l'extraction.
                                </p>
                            </CardHeader>
                            <CardBody>
                                <Form onSubmit={handleProcess}>
                                    <Row>
                                        <Col md="5">
                                            <FormGroup>
                                                <label>Activité / Métier</label>
                                                <Input
                                                    placeholder="Ex: Plomberie, Restaurant..."
                                                    type="text"
                                                    value={searchTerm}
                                                    onChange={(e) => setSearchTerm(e.target.value)}
                                                />
                                            </FormGroup>
                                        </Col>
                                        <Col md="3">
                                            <FormGroup>
                                                <label>Code Postal</label>
                                                <Input
                                                    placeholder="Ex: 69400"
                                                    type="text"
                                                    value={zipCode}
                                                    onChange={(e) => setZipCode(e.target.value)}
                                                />
                                            </FormGroup>
                                        </Col>
                                        <Col md="4" className="d-flex align-items-center">
                                            <Button
                                                color="primary"
                                                type="submit"
                                                disabled={isProcessing}
                                                block
                                                style={{ marginTop: "15px" }}
                                            >
                                                {isProcessing ? (
                                                    <>
                                                        <Spinner size="sm" className="mr-2" />
                                                        Scraping...
                                                    </>
                                                ) : (
                                                    "Lancer l'extraction"
                                                )}
                                            </Button>
                                        </Col>
                                    </Row>
                                </Form>
                            </CardBody>
                        </Card>
                    </Col>
                </Row>
                <Row>
                    <Col md="12">
                        <Card>
                            <CardHeader className="d-flex justify-content-between align-items-center">
                                <CardTitle tag="h4">Résultats des Dirigeants</CardTitle>
                                <div>
                                    <Button color="info" size="sm" onClick={fetchResults} className="mr-2">
                                        Actualiser
                                    </Button>
                                    <Button color="success" size="sm" href={`${API_URL}/results`} download>
                                        Exporter CSV
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardBody>
                                <Table responsive>
                                    <thead className="text-primary">
                                        <tr>
                                            <th>Entreprise</th>
                                            <th>Dirigeant(s)</th>
                                            <th>Ville</th>
                                            <th>Téléphone</th>
                                            <th className="text-right">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {loading ? (
                                            <tr>
                                                <td colSpan="5" className="text-center py-5">
                                                    <Spinner color="primary" />
                                                </td>
                                            </tr>
                                        ) : results.length > 0 ? (
                                            results.map((row, idx) => (
                                                <tr key={idx}>
                                                    <td>
                                                        <div className="font-weight-bold">{row.Nom || "N/A"}</div>
                                                        <small className="text-muted">SIRET: {row.SIRET || "Inconnu"}</small>
                                                    </td>
                                                    <td className={row.Dirigeants ? "text-info" : "text-muted italic"}>
                                                        {row.Dirigeants || "Non trouvé"}
                                                    </td>
                                                    <td>
                                                        <div>{row.Adresse || "N/A"}</div>
                                                    </td>
                                                    <td>
                                                        {row.Téléphone || row["Téléphone trouvé sur site"] ? (
                                                            <span className="badge badge-success px-2 py-1">
                                                                {row.Téléphone || row["Téléphone trouvé sur site"]}
                                                            </span>
                                                        ) : (
                                                            <span className="text-muted small">Aucun numéro</span>
                                                        )}
                                                    </td>
                                                    <td className="text-right">
                                                        {row["Site web"] && (
                                                            <a
                                                                href={row["Site web"].startsWith("http") ? row["Site web"] : `https://${row["Site web"]}`}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="btn btn-sm btn-outline-primary btn-icon mr-1"
                                                                title="Site Web"
                                                            >
                                                                <i className="fa fa-globe" />
                                                            </a>
                                                        )}
                                                        {row["Lien Pappers"] && (
                                                            <a
                                                                href={row["Lien Pappers"]}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="btn btn-sm btn-outline-info btn-icon"
                                                                title="Pappers"
                                                            >
                                                                <i className="fa fa-external-link" />
                                                            </a>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan="5" className="text-center py-5 text-muted">
                                                    Aucun prospect trouvé. Lancez une recherche.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </Table>
                            </CardBody>
                        </Card>
                    </Col>
                </Row>
            </div>
        </>
    );
}

export default Prospects;
