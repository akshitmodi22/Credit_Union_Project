import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { X, Info } from 'lucide-react'
import { getModelHealth } from '../api'

const MODEL_DETAILS = {
  attrition: {
    title: 'Attrition Risk Model',
    objective: 'Predict which members are likely to churn (leave the credit union) in the next 90 days.',
    algorithm: 'RandomForest (n_estimators=200, max_depth=10, class_weight=balanced)',
    target: 'churned (binary: 0 = Stayed, 1 = Churned)',
    inputTables: [
      'cu_members.csv — demographics (branch, county, age, income, life stage)',
      'cu_products.csv — product holdings (checking, savings, loans, CDs)',
      'cu_behavior.csv — 6-month behavioral snapshots (balances, transactions)',
      'cu_digital_activity.csv — digital engagement (logins, transfers, bill pay)',
      'cu_marketing_engagement.csv — campaign responses, offer history',
      'cu_derived_features.csv — risk composite, engagement index, flags',
    ],
    keyFeatures: [
      'Behavioral trends (balance changes across 6 months)',
      'Transaction frequency & channel mix',
      'Digital engagement (logins, app opens, online transfers)',
      'Campaign response rates',
      'Social sentiment scores (30d, 90d)',
      'Product depth & relationship breadth',
      'Direct deposit status',
      'Risk composite & engagement index',
    ],
    output: [
      'attrition_probability — churn likelihood (0.0–1.0)',
      'attrition_tier — High (≥0.7) / Medium (0.4–0.7) / Low (<0.4)',
      'shap_reason_1 through shap_reason_10 — top SHAP explanations per member',
    ],
    preprocessing: 'Median imputation for numeric nulls, mode for categorical. One-hot encoding for categoricals. Dropped leaky columns (month6 snapshots, derived flags, balance_trend_3mo).',
    sampling: 'class_weight=balanced (built-in)',
  },

  loan: {
    title: 'Loan Offer Propensity Model',
    objective: 'Predict which members will accept a loan offer if presented one.',
    algorithm: 'XGBoost (n_estimators=300, max_depth=5, learning_rate=0.05, SMOTE)',
    target: 'accepted_loan (binary: 0 = Declined, 1 = Accepted)',
    inputTables: [
      'cu_members.csv — demographics',
      'cu_products.csv — product holdings',
      'cu_behavior.csv — latest behavioral snapshot',
      'cu_digital_activity.csv — digital engagement',
      'cu_marketing_engagement.csv — campaign responses (cleaned: offer_accepted_flag, last_offer_type dropped)',
      'cu_derived_features.csv — risk composite, engagement metrics',
    ],
    keyFeatures: [
      'Credit score band & income band',
      'Digital logins & app engagement',
      'Overdraft count & risk composite',
      'Number of products held',
      'Savings & checking balances',
      'Direct deposit status',
      'Campaign email & SMS open rates',
      'Relationship depth score',
    ],
    output: [
      'loan_offer_score — acceptance probability (0.0–1.0)',
      'loan_offer_tier — High (≥0.7) / Medium (0.4–0.7) / Low (<0.4)',
      'status — never_offered / offered_accepted / offered_declined',
      'shap_reason_1 through shap_reason_10 — top SHAP explanations',
    ],
    preprocessing: 'LabelEncoder for categoricals. Dropped leaky columns (was_offered, accepted_loan, campaign_response, balance_trend_3mo, churned).',
    sampling: 'SMOTE oversampling on training set',
  },

  propensity: {
    title: 'Deposit Propensity Model',
    objective: 'Predict which members are likely to open a new Certificate of Deposit (CD).',
    algorithm: 'XGBoost (n_estimators=300, max_depth=5, learning_rate=0.05)',
    target: 'deposit_propensity_label (binary: 0 = No CD, 1 = Likely CD)',
    inputTables: [
      'cu_members.csv — demographics',
      'cu_products.csv — product holdings',
      'cu_behavior.csv — latest behavioral snapshot',
      'cu_digital_activity.csv — digital engagement',
      'cu_marketing_engagement.csv — campaign responses (cleaned)',
      'cu_derived_features.csv — risk composite, engagement metrics',
    ],
    keyFeatures: [
      'Savings balance & balance trend (90d)',
      'Financial readiness score (savings > $3k, no existing CD)',
      'Behavioral engagement (digital logins, transaction frequency)',
      'Relationship depth (number of products, tenure)',
      'Life stage indicators (young_single, established, pre_retirement)',
      'Income band & credit score band',
      'Direct deposit & bill pay usage',
      'Campaign engagement history',
    ],
    output: [
      'propensity_probability — CD likelihood (0.0–1.0)',
      'propensity_tier — High (≥0.7) / Medium (0.4–0.7) / Low (<0.4)',
      'shap_reason_1 through shap_reason_10 — top SHAP explanations',
    ],
    preprocessing: 'LabelEncoder for categoricals. Dropped leaky columns (has_cd, cd_balance, churned, top_reason). Hard exclusions applied during label engineering.',
    sampling: 'Weighted scoring system with sigmoid + Gaussian noise (~18% positive rate)',
  },
}

function Section({ label, children }) {
  return (
    <div className="mb-4">
      <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">{label}</div>
      <div className="text-[12px] text-gray-700 leading-relaxed">{children}</div>
    </div>
  )
}

export default function ModelInfoModal({ model, onClose }) {
  const details = MODEL_DETAILS[model]
  if (!details) return null

  const { data: healthData } = useQuery({
    queryKey: ['model-health-modal'],
    queryFn: getModelHealth,
    staleTime: 60000,
  })

  const info = healthData?.models?.[model] || {}

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-[680px] max-h-[85vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between flex-shrink-0 bg-gray-50">
          <div>
            <div className="text-base font-bold text-gray-900">{details.title}</div>
            <div className="text-[11px] text-gray-400 mt-0.5 font-mono">
              {info.version ? `v${info.version}` : ''} · AUC: {info.auc || '—'} · Status: {' '}
              <span className={info.status === 'healthy' ? 'text-green-600' : 'text-amber-600'}>{info.status || '—'}</span>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors">
            <X size={16} className="text-gray-500" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 overflow-y-auto flex-1">

          {/* Status pills */}
          <div className="flex gap-3 mb-5">
            <div className="flex-1 bg-blue-50 border border-blue-100 rounded-lg px-3 py-2 text-center">
              <div className="text-[10px] text-blue-400 font-medium">Last Trained</div>
              <div className="text-sm font-bold text-blue-700 font-mono">{info.trained_on || '—'}</div>
            </div>
            <div className="flex-1 bg-purple-50 border border-purple-100 rounded-lg px-3 py-2 text-center">
              <div className="text-[10px] text-purple-400 font-medium">Last Predicted</div>
              <div className="text-sm font-bold text-purple-700 font-mono">{info.predicted_on || '—'}</div>
            </div>
            <div className={`flex-1 rounded-lg px-3 py-2 text-center border ${info.status === 'healthy' ? 'bg-green-50 border-green-100' : 'bg-amber-50 border-amber-100'}`}>
              <div className={`text-[10px] font-medium ${info.status === 'healthy' ? 'text-green-400' : 'text-amber-400'}`}>AUC Score</div>
              <div className={`text-sm font-bold font-mono ${info.status === 'healthy' ? 'text-green-700' : 'text-amber-700'}`}>{info.auc || '—'}</div>
            </div>
          </div>

          <Section label="Objective">{details.objective}</Section>
          <Section label="Algorithm">{details.algorithm}</Section>
          <Section label="Target Variable">
            <code className="bg-gray-100 px-1.5 py-0.5 rounded text-[11px] font-mono">{details.target}</code>
          </Section>

          <Section label="Input Data (6 Tables)">
            <div className="flex flex-col gap-1">
              {details.inputTables.map((t, i) => (
                <div key={i} className="flex items-start gap-2 text-[11px]">
                  <span className="text-gray-300 mt-0.5">›</span>
                  <span><code className="bg-gray-100 px-1 py-0.5 rounded text-[10px] font-mono">{t.split(' — ')[0]}</code> — {t.split(' — ')[1]}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section label="Key Features">
            <div className="grid grid-cols-2 gap-1">
              {details.keyFeatures.map((f, i) => (
                <div key={i} className="flex items-start gap-1.5 text-[11px]">
                  <span className="text-brand-500 mt-0.5">•</span>
                  <span>{f}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section label="Output">
            <div className="flex flex-col gap-1">
              {details.output.map((o, i) => (
                <div key={i} className="flex items-start gap-2 text-[11px]">
                  <span className="text-green-500 mt-0.5">→</span>
                  <span><code className="bg-gray-100 px-1 py-0.5 rounded text-[10px] font-mono">{o.split(' — ')[0]}</code> — {o.split(' — ')[1]}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section label="Preprocessing">{details.preprocessing}</Section>
          <Section label="Sampling Strategy">{details.sampling}</Section>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-gray-100 bg-gray-50 flex-shrink-0">
          <div className="text-[9px] text-gray-400 font-mono">
            Credit Union Intelligence · IBM watsonx.ai · Model documentation auto-generated
          </div>
        </div>
      </div>
    </div>
  )
}


// Small info button to trigger the modal
export function ModelInfoButton({ model, onClick }) {
  return (
    <button
      onClick={(e) => { e.stopPropagation(); onClick(model) }}
      className="p-0.5 hover:bg-gray-200 rounded transition-colors"
      title={`View ${model} model details`}
    >
      <Info size={12} className="text-gray-400 hover:text-brand-600" />
    </button>
  )
}