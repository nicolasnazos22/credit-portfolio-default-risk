package com.creditportfolio.defaultrisk.springbootmicroservice.domain.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.util.UUID;
public class CreditInferenceExplanation {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "request_id", nullable = false)
    private UUID requestId;

    @Column(nullable = false)
    private String feature;

    @Column(name = "shap_value", nullable = false)
    private Double shapValue;
    protected CreditInferenceExplanation() { }
    public CreditInferenceExplanation(UUID requestId, String feature, Double shapValue) {
        this.requestId = requestId;
        this.feature = feature;
        this.shapValue = shapValue;
    }
   
    public UUID getId() { return id; }
    public UUID getRequestId() { return requestId; }
    public String getFeature() { return feature; }
    public Double getShapValue() { return shapValue; }
}
