package com.creditportfolio.defaultrisk.springbootmicroservice.domain.entity;
import com.creditportfolio.defaultrisk.springbootmicroservice.domain.enums.DecisionCredito;
import com.creditportfolio.defaultrisk.springbootmicroservice.domain.enums.EtiquetaRiesgo;
import com.creditportfolio.defaultrisk.springbootmicroservice.domain.enums.StatusInferencia;
import jakarta.persistence.*;
import java.util.UUID;
import java.time.Instant;

@Entity
@Table(name = "credit_inferences")
public class CreditInference{
    @Id
    private UUID requestId;

    @Column(nullable = false)
    private Long userId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private StatusInferencia status;

    @Column(name="probabilidad_default")
    private Double probabilidadDefault;

    @Enumerated(EnumType.STRING)
    @Column(name= "etiqueta_riesgo")
    private EtiquetaRiesgo etiquetaRiesgo;

    @Enumerated(EnumType.STRING)
    @Column(name= "decision_final")
    private DecisionCredito decisionFinal;

    @Column(name="created_at", updatable = false)
    private Instant createdAt;
    
    @OneToOne(mappedBy = "inference",
            cascade = CascadeType.ALL,
            orphanRemoval = true)
    private CreditInferenceFeatures features;
    
    protected CreditInference() {
    } 
    public CreditInference(UUID requestId, Long userId) {
        this.requestId = requestId;
        this.userId = userId;
        this.status = StatusInferencia.PENDIENTE;
        this.createdAt = Instant.now();
    }

    public void otorgarCredito(int prediccionModelo, double ProbabilidadDefault, EtiquetaRiesgo etiquetaRiesgo) {
        this.probabilidadDefault = ProbabilidadDefault;
        this.etiquetaRiesgo = etiquetaRiesgo;
        this.decisionFinal = (prediccionModelo == 1) ? DecisionCredito.ACEPTADO : DecisionCredito.RECHAZADO;
        this.status = StatusInferencia.COMPLETADO;
    }
    public UUID getRequestId() { return requestId; }
    
    public Long getUserId() { return userId; }
    
    public StatusInferencia getStatus() { return status; }
    public void setStatus(StatusInferencia status) { this.status = status; }
    
    public Double getProbabilidadDefault() { return probabilidadDefault; }
    public void setProbabilidadDefault(Double probabilidadDefault) { this.probabilidadDefault = probabilidadDefault; }
    
    public EtiquetaRiesgo getEtiquetaRiesgo() { return etiquetaRiesgo; }
    public void setEtiquetaRiesgo(EtiquetaRiesgo etiquetaRiesgo) { this.etiquetaRiesgo = etiquetaRiesgo; }
    
    public DecisionCredito getDecisionFinal() { return decisionFinal; }
    
    public Instant getCreatedAt() { return createdAt; }
    public void setFeatures(CreditInferenceFeatures features) {
        this.features = features;
    }
    public void getFeatures() {
        return features;
    }
}
