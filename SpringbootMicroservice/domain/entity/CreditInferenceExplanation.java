com.creditportfolio.defaultrisk.springbootmicroservice.domain.entity.CreditInferenceExplanation
@entity
@Table(name = "credit_inference_explanations")
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

    public CreditInferenceExplanation(UUID requestId, String feature, Double shapValue) {
        this.requestId = requestId;
        this.feature = feature;
        this.shapValue = shapValue;
    }
    public UUID getId() { return id; }
    public getRequestId() { return requestId; }
    public String getFeature() { return feature; }
    public Double getShapValue() { return shapValue; }
}
