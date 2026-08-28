package com.creditportfolio.defaultrisk.springbootmicroservice.domain.entity;

import com.creditportfolio.defaultrisk.springbootmicroservice.domain.enums.CbDefaultOnFile;
import com.creditportfolio.defaultrisk.springbootmicroservice.domain.enums.HomeOwnership;
import com.creditportfolio.defaultrisk.springbootmicroservice.domain.enums.LoanGrade;
import com.creditportfolio.defaultrisk.springbootmicroservice.domain.enums.LoanIntent;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.MapsId;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

import java.util.UUID;

@Entity
@Table(name = "credit_inference_features")
public class CreditInferenceFeatures {

    @Id
    @Column(name = "inference_id", nullable = false)
    private UUID inferenceId;

    @OneToOne
    @MapsId
    @JoinColumn(name = "inference_id")
    private CreditInference inference;

    @Column(name = "person_age", nullable = false)
    private Integer personAge;

    @Column(name = "person_income", nullable = false)
    private Integer personIncome;

    @Enumerated(EnumType.STRING)
    @Column(name = "person_home_ownership", nullable = false)
    private HomeOwnership personHomeOwnership;

    @Column(name = "person_emp_length", nullable = false)
    private Double personEmpLength;

    @Enumerated(EnumType.STRING)
    @Column(name = "loan_intent", nullable = false)
    private LoanIntent loanIntent;

    @Enumerated(EnumType.STRING)
    @Column(name = "loan_grade", nullable = false)
    private LoanGrade loanGrade;

    @Column(name = "loan_amnt", nullable = false)
    private Integer loanAmnt;

    @Column(name = "loan_int_rate", nullable = false)
    private Double loanIntRate;

    @Column(name = "loan_percent_income", nullable = false)
    private Double loanPercentIncome;

    @Column(name = "cb_person_cred_hist_length", nullable = false)
    private Integer cbPersonCredHistLength;

    @Enumerated(EnumType.STRING)
    @Column(name = "cb_person_default_on_file", nullable = false)
    private CbDefaultOnFile cbPersonDefaultOnFile;

    protected CreditInferenceFeatures() {
    }

    public CreditInferenceFeatures(
            CreditInference inference,
            Integer personAge,
            Integer personIncome,
            HomeOwnership personHomeOwnership,
            Double personEmpLength,
            LoanIntent loanIntent,
            LoanGrade loanGrade,
            Integer loanAmnt,
            Double loanIntRate,
            Double loanPercentIncome,
            Integer cbPersonCredHistLength,
            CbDefaultOnFile cbPersonDefaultOnFile
    ) {
        this.inference = inference;
        this.personAge = personAge;
        this.personIncome = personIncome;
        this.personHomeOwnership = personHomeOwnership;
        this.personEmpLength = personEmpLength;
        this.loanIntent = loanIntent;
        this.loanGrade = loanGrade;
        this.loanAmnt = loanAmnt;
        this.loanIntRate = loanIntRate;
        this.loanPercentIncome = loanPercentIncome;
        this.cbPersonCredHistLength = cbPersonCredHistLength;
        this.cbPersonDefaultOnFile = cbPersonDefaultOnFile;
    }

    public UUID getInferenceId() {
        return inferenceId;
    }

    public CreditInference getInference() {
        return inference;
    }

    public Integer getPersonAge() {
        return personAge;
    }

    public Integer getPersonIncome() {
        return personIncome;
    }

    public HomeOwnership getPersonHomeOwnership() {
        return personHomeOwnership;
    }

    public Double getPersonEmpLength() {
        return personEmpLength;
    }

    public LoanIntent getLoanIntent() {
        return loanIntent;
    }

    public LoanGrade getLoanGrade() {
        return loanGrade;
    }

    public Integer getLoanAmnt() {
        return loanAmnt;
    }

    public Double getLoanIntRate() {
        return loanIntRate;
    }

    public Double getLoanPercentIncome() {
        return loanPercentIncome;
    }

    public Integer getCbPersonCredHistLength() {
        return cbPersonCredHistLength;
    }

    public CbDefaultOnFile getCbPersonDefaultOnFile() {
        return cbPersonDefaultOnFile;
    }
}