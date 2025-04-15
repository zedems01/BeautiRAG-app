'use client';

import React, { useState, useEffect } from 'react';

// Eye Icons
const EyeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
  </svg>
);

const EyeOffIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
  </svg>
);

// Define props for the component
interface ModelSelectionProps {
  onConfigValidated: (model: string, apiKey: string) => void; 
  defaultModel?: string; // Optional initial model
}

const ModelSelection: React.FC<ModelSelectionProps> = ({ onConfigValidated, defaultModel }) => {
  // Internal state for model selection and API key
  const [selectedModel, setSelectedModel] = useState<string>(defaultModel || 'gpt-4o');
  const [apiKey, setApiKey] = useState<string>('');
  const [isApiKeyVisible, setIsApiKeyVisible] = useState(false);
  const [validationMessage, setValidationMessage] = useState<string>('');

  // Reset API key and message if defaultModel prop changes
  useEffect(() => {
    setSelectedModel(defaultModel || 'gpt-4o');
    setApiKey('');
    setValidationMessage('');
  }, [defaultModel]);

  // Model list
  const models = {
    OpenAI: ['gpt-4o', 'gpt-4o-mini', 'o1-mini', 'o3-mini'],
    Anthropic: ['claude-3-sonnet-latest', 'claude-3-haiku-latest'],
    DeepSeek: ['deepseek-chat'],
    Ollama: ['llama3', 'mistral', 'gemma'],  // to be integrated furthur
  };

  // Helper to flatten the models object for the dropdown
  const allModelOptions = Object.entries(models).flatMap(([provider, modelList]) =>
    modelList.map(model => ({ value: model, label: `${model} (${provider})` }))
  );

  // Function to find the provider of a given model name
  const getProviderForModel = (modelName: string): string | null => {
    for (const [provider, modelList] of Object.entries(models)) {
      if (modelList.includes(modelName)) {
        return provider; // Return the provider name (e.g., 'OpenAI', 'Ollama')
      }
    }
    return null; // Model not found in our list
  };

  // Determine if the currently selected model requires an API key
  const providerOfSelectedModel = getProviderForModel(selectedModel);

  // Only models from the 'Ollama' provider do NOT require an API key.
  // All other providers, or if the provider is unknown, will require a key.
  const requiresApiKey = providerOfSelectedModel !== 'Ollama';


  const handleModelChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedModel(event.target.value);
    setApiKey(''); // Reset API key when model changes
    setIsApiKeyVisible(false);
    setValidationMessage(''); // Clear validation message
  };

  const handleApiKeyChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setApiKey(event.target.value);
    setValidationMessage(''); // Clear validation message
  };

  const handleValidate = () => {
    if (requiresApiKey && !apiKey.trim()) {
      setValidationMessage('API key is required for this model.');
      return;
    }
    // Call the callback prop passed from the parent
    onConfigValidated(selectedModel, apiKey);
    setValidationMessage('Configuration applied successfully!');
    
    // Clear the API key field and reset visibility after successful validation
    setApiKey('');
    setIsApiKeyVisible(false);

    // Clear message after a few seconds
    setTimeout(() => setValidationMessage(''), 5000);
  };


  return (
    <div className="bg-gray-850 border border-gray-700 p-6 rounded-lg shadow-md text-gray-200 flex flex-col">
      <h2 className="text-xl font-semi-bold-serif mb-4 text-white">AI Model Selection</h2>
      <div className="flex-grow">
        <div className="mb-4">
          <label htmlFor="model-select" className="block text-sm font-medium text-gray-300 mb-1">Select Model:</label>
          <select
            id="model-select"
            value={selectedModel}
            onChange={handleModelChange}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-white appearance-none"
            style={{ backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.5rem center', backgroundSize: '1.5em 1.5em' }}
          >
            {allModelOptions.map(opt => (
              <option key={opt.value} value={opt.value} className="bg-gray-800 text-white">
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {requiresApiKey && (
          <div className="flex items-end gap-2 mb-4">
            <div className="flex-grow">
              <label htmlFor="api-key-input" className="block text-sm font-medium text-gray-300 mb-1">API Key:</label>
              <div className="relative">
                <input
                  type={isApiKeyVisible ? 'text' : 'password'}
                  id="api-key-input"
                  value={apiKey}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your API key"
                  className="w-full pl-3 pr-10 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-white placeholder-gray-500"
                />
                <button
                  type="button"
                  onClick={() => setIsApiKeyVisible(!isApiKeyVisible)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-200"
                  aria-label={isApiKeyVisible ? "Hide API key" : "Show API key"}
                >
                  {isApiKeyVisible ? <EyeOffIcon /> : <EyeIcon />}
                </button>
              </div>
            </div>
            <button
              onClick={handleValidate}
              disabled={!apiKey.trim()}
              className="flex-shrink-0 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-850 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150"
            >
              Validate
            </button>
          </div>
        )}
      </div>

      {/* Validation Message */}
      {validationMessage && (
        <p className={`text-sm mt-2 mb-3 ${validationMessage.includes('required') ? 'text-red-400' : 'text-green-400'}`}>
          {validationMessage}
        </p>
      )}
    </div>
  );
};

export default ModelSelection; 