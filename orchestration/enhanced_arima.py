import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from scipy import stats
import matplotlib.pyplot as plt
import logging
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ARIMAModel:
    """ARIMA model configuration"""
    p: int = 1  # AR order
    d: int = 1  # Differencing order
    q: int = 1  # MA order
    P: int = 1  # Seasonal AR order
    D: int = 1  # Seasonal differencing order
    Q: int = 1  # Seasonal MA order
    s: int = 12  # Seasonal period

@dataclass
class ForecastResult:
    """Forecast result with confidence intervals"""
    forecast: np.ndarray
    lower_ci: np.ndarray
    upper_ci: np.ndarray
    confidence_level: float
    model_aic: float
    model_bic: float
    accuracy_metrics: Dict[str, float]

class EnhancedARIMAForecaster:
    """Enhanced ARIMA forecaster with seasonal components and adaptive parameters"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.model = None
        self.fitted_model = None
        self.history = []
        self.forecast_history = []
        self.model_performance = []
        
        # Default parameters
        self.min_history_length = self.config.get('min_history_length', 20)
        self.max_history_length = self.config.get('max_history_length', 1000)
        self.forecast_horizon = self.config.get('forecast_horizon', 12)
        self.confidence_level = self.config.get('confidence_level', 0.95)
        self.auto_optimize = self.config.get('auto_optimize', True)
        
        # Seasonal patterns
        self.seasonal_patterns = {
            'hourly': 24,
            'daily': 7,
            'weekly': 4,
            'monthly': 12,
            'quarterly': 4
        }
        
    def add_data_point(self, value: float, timestamp: Optional[str] = None):
        """Add new data point to history"""
        if timestamp:
            self.history.append({'timestamp': timestamp, 'value': value})
        else:
            self.history.append({'timestamp': len(self.history), 'value': value})
        
        # Maintain history length
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length:]
        
        logger.debug(f"Added data point: {value}, history length: {len(self.history)}")
    
    def _prepare_data(self) -> np.ndarray:
        """Prepare data for ARIMA modeling"""
        if len(self.history) < self.min_history_length:
            raise ValueError(f"Insufficient data. Need at least {self.min_history_length} points")
        
        # Extract values
        values = [point['value'] for point in self.history]
        return np.array(values)
    
    def _check_stationarity(self, data: np.ndarray) -> Dict[str, float]:
        """Check data stationarity using ADF and KPSS tests"""
        # Augmented Dickey-Fuller test
        adf_result = adfuller(data)
        adf_statistic = adf_result[0]
        adf_pvalue = adf_result[1]
        
        # KPSS test
        kpss_result = kpss(data)
        kpss_statistic = kpss_result[0]
        kpss_pvalue = kpss_result[1]
        
        return {
            'adf_statistic': adf_statistic,
            'adf_pvalue': adf_pvalue,
            'kpss_statistic': kpss_statistic,
            'kpss_pvalue': kpss_pvalue,
            'is_stationary': adf_pvalue < 0.05 and kpss_pvalue > 0.05
        }
    
    def _determine_differencing(self, data: np.ndarray) -> int:
        """Determine optimal differencing order"""
        d = 0
        current_data = data.copy()
        
        while d <= 2:  # Maximum 2nd order differencing
            stationarity = self._check_stationarity(current_data)
            
            if stationarity['is_stationary']:
                break
            
            # Apply differencing
            current_data = np.diff(current_data)
            d += 1
        
        logger.info(f"Determined differencing order: d={d}")
        return d
    
    def _find_optimal_parameters(self, data: np.ndarray) -> ARIMAModel:
        """Find optimal ARIMA parameters using grid search"""
        if not self.auto_optimize:
            return ARIMAModel()
        
        best_aic = float('inf')
        best_model = ARIMAModel()
        
        # Grid search for non-seasonal parameters
        p_values = range(0, 4)
        q_values = range(0, 4)
        
        # Seasonal parameters (if data length allows)
        seasonal_periods = [12] if len(data) >= 50 else [1]
        
        for p in p_values:
            for q in q_values:
                for s in seasonal_periods:
                    try:
                        # Determine differencing
                        d = self._determine_differencing(data)
                        D = 1 if s > 1 else 0
                        
                        # Try different seasonal parameters
                        for P in range(0, min(3, len(data) // s)):
                            for Q in range(0, min(3, len(data) // s)):
                                try:
                                    model = ARIMA(data, order=(p, d, q), 
                                                seasonal_order=(P, D, Q, s))
                                    fitted_model = model.fit()
                                    
                                    if fitted_model.aic < best_aic:
                                        best_aic = fitted_model.aic
                                        best_model = ARIMAModel(p, d, q, P, D, Q, s)
                                        
                                except:
                                    continue
                                    
                    except:
                        continue
        
        logger.info(f"Optimal parameters: {best_model}")
        return best_model
    
    def _fit_model(self, data: np.ndarray, model_config: ARIMAModel) -> ARIMA:
        """Fit ARIMA model with given parameters"""
        try:
            model = ARIMA(data, order=(model_config.p, model_config.d, model_config.q),
                         seasonal_order=(model_config.P, model_config.D, model_config.Q, model_config.s))
            
            fitted_model = model.fit()
            
            # Model diagnostics
            residuals = fitted_model.resid
            ljung_box = acorr_ljungbox(residuals, lags=10, return_df=True)
            
            # Check residuals normality
            _, normality_pvalue = stats.normaltest(residuals)
            
            diagnostics = {
                'ljung_box_pvalue': ljung_box['lb_pvalue'].iloc[-1],
                'normality_pvalue': normality_pvalue,
                'aic': fitted_model.aic,
                'bic': fitted_model.bic
            }
            
            logger.info(f"Model fitted successfully. AIC: {fitted_model.aic:.3f}, BIC: {fitted_model.bic:.3f}")
            logger.info(f"Residual diagnostics - Ljung-Box p-value: {diagnostics['ljung_box_pvalue']:.3f}")
            
            return fitted_model, diagnostics
            
        except Exception as e:
            logger.error(f"Error fitting ARIMA model: {e}")
            raise
    
    def _calculate_confidence_intervals(self, forecast_result, confidence_level: float) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate confidence intervals for forecast"""
        # Get forecast standard errors
        forecast_std = forecast_result.params.get('forecast_std', None)
        
        if forecast_std is None:
            # Use historical residuals for confidence intervals
            residuals = self.fitted_model.resid
            residual_std = np.std(residuals)
            
            # Simple confidence intervals based on residual standard deviation
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            margin_of_error = z_score * residual_std
            
            lower_ci = forecast_result.forecast - margin_of_error
            upper_ci = forecast_result.forecast + margin_of_error
        else:
            # Use model-provided confidence intervals
            lower_ci = forecast_result.forecast - forecast_std
            upper_ci = forecast_result.forecast + forecast_std
        
        return lower_ci, upper_ci
    
    def _calculate_accuracy_metrics(self, actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
        """Calculate forecast accuracy metrics"""
        if len(actual) != len(predicted):
            min_len = min(len(actual), len(predicted))
            actual = actual[:min_len]
            predicted = predicted[:min_len]
        
        # Mean Absolute Error
        mae = np.mean(np.abs(actual - predicted))
        
        # Mean Squared Error
        mse = np.mean((actual - predicted) ** 2)
        rmse = np.sqrt(mse)
        
        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        
        # Symmetric Mean Absolute Percentage Error
        smape = 2 * np.mean(np.abs(actual - predicted) / (np.abs(actual) + np.abs(predicted))) * 100
        
        # R-squared
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'mape': mape,
            'smape': smape,
            'r_squared': r_squared
        }
    
    def forecast(self, steps: Optional[int] = None) -> ForecastResult:
        """Generate forecast with confidence intervals"""
        if len(self.history) < self.min_history_length:
            raise ValueError(f"Insufficient data for forecasting. Need at least {self.min_history_length} points")
        
        steps = steps or self.forecast_horizon
        data = self._prepare_data()
        
        # Find optimal parameters
        model_config = self._find_optimal_parameters(data)
        
        # Fit model
        self.fitted_model, diagnostics = self._fit_model(data, model_config)
        
        # Generate forecast
        forecast_result = self.fitted_model.forecast(steps=steps)
        
        # Calculate confidence intervals
        lower_ci, upper_ci = self._calculate_confidence_intervals(forecast_result, self.confidence_level)
        
        # Store forecast
        forecast_data = {
            'timestamp': len(self.history),
            'forecast': forecast_result,
            'lower_ci': lower_ci,
            'upper_ci': upper_ci,
            'model_config': model_config,
            'diagnostics': diagnostics
        }
        self.forecast_history.append(forecast_data)
        
        # Calculate accuracy metrics if we have recent actual data
        accuracy_metrics = {}
        if len(self.history) >= steps:
            recent_actual = data[-steps:]
            accuracy_metrics = self._calculate_accuracy_metrics(recent_actual, forecast_result)
        
        result = ForecastResult(
            forecast=forecast_result,
            lower_ci=lower_ci,
            upper_ci=upper_ci,
            confidence_level=self.confidence_level,
            model_aic=diagnostics['aic'],
            model_bic=diagnostics['bic'],
            accuracy_metrics=accuracy_metrics
        )
        
        logger.info(f"Forecast generated for {steps} steps")
        if accuracy_metrics:
            logger.info(f"Accuracy - RMSE: {accuracy_metrics.get('rmse', 0):.3f}, "
                       f"MAPE: {accuracy_metrics.get('mape', 0):.3f}%")
        
        return result
    
    def update_model(self):
        """Update model with new data"""
        if len(self.history) < self.min_history_length:
            return
        
        # Retrain model with updated data
        data = self._prepare_data()
        model_config = self._find_optimal_parameters(data)
        self.fitted_model, _ = self._fit_model(data, model_config)
        
        logger.info("Model updated with new data")
    
    def get_forecast_summary(self) -> Dict:
        """Get summary of recent forecasts"""
        if not self.forecast_history:
            return {}
        
        latest_forecast = self.forecast_history[-1]
        
        return {
            'latest_forecast': latest_forecast['forecast'].tolist(),
            'confidence_intervals': {
                'lower': latest_forecast['lower_ci'].tolist(),
                'upper': latest_forecast['upper_ci'].tolist()
            },
            'model_parameters': {
                'p': latest_forecast['model_config'].p,
                'd': latest_forecast['model_config'].d,
                'q': latest_forecast['model_config'].q,
                'P': latest_forecast['model_config'].P,
                'D': latest_forecast['model_config'].D,
                'Q': latest_forecast['model_config'].Q,
                's': latest_forecast['model_config'].s
            },
            'model_quality': {
                'aic': latest_forecast['diagnostics']['aic'],
                'bic': latest_forecast['diagnostics']['bic']
            },
            'accuracy_metrics': latest_forecast.get('accuracy_metrics', {})
        }
    
    def plot_forecast(self, save_path: Optional[str] = None):
        """Plot forecast with confidence intervals"""
        if not self.forecast_history:
            logger.warning("No forecast history available for plotting")
            return
        
        latest_forecast = self.forecast_history[-1]
        data = self._prepare_data()
        
        plt.figure(figsize=(12, 8))
        
        # Plot historical data
        plt.plot(range(len(data)), data, 'b-', label='Historical Data', linewidth=2)
        
        # Plot forecast
        forecast_start = len(data)
        forecast_end = forecast_start + len(latest_forecast['forecast'])
        plt.plot(range(forecast_start, forecast_end), latest_forecast['forecast'], 
                'r--', label='Forecast', linewidth=2)
        
        # Plot confidence intervals
        plt.fill_between(range(forecast_start, forecast_end),
                        latest_forecast['lower_ci'],
                        latest_forecast['upper_ci'],
                        alpha=0.3, color='red', label=f'{self.confidence_level*100:.0f}% Confidence Interval')
        
        plt.title('ARIMA Forecast with Confidence Intervals')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Forecast plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def get_scaling_recommendations(self, current_load: float, threshold: float = 0.8) -> Dict:
        """Get scaling recommendations based on forecast"""
        if not self.forecast_history:
            return {'action': 'maintain', 'reason': 'No forecast available'}
        
        latest_forecast = self.forecast_history[-1]
        forecast_values = latest_forecast['forecast']
        
        # Calculate forecast statistics
        max_forecast = np.max(forecast_values)
        mean_forecast = np.mean(forecast_values)
        trend = np.polyfit(range(len(forecast_values)), forecast_values, 1)[0]
        
        # Determine scaling action
        if max_forecast > threshold:
            if trend > 0:
                action = 'scale_out'
                reason = f'Forecast shows increasing trend (slope: {trend:.3f}) and peak load {max_forecast:.3f} exceeds threshold'
            else:
                action = 'scale_out'
                reason = f'Peak forecast load {max_forecast:.3f} exceeds threshold despite decreasing trend'
        elif mean_forecast < threshold * 0.5 and trend < 0:
            action = 'scale_in'
            reason = f'Forecast shows decreasing trend and low average load {mean_forecast:.3f}'
        else:
            action = 'maintain'
            reason = f'Forecast within acceptable range (mean: {mean_forecast:.3f}, max: {max_forecast:.3f})'
        
        return {
            'action': action,
            'reason': reason,
            'forecast_stats': {
                'max_load': max_forecast,
                'mean_load': mean_forecast,
                'trend': trend,
                'confidence_level': self.confidence_level
            },
            'current_load': current_load,
            'threshold': threshold
        }

# Example usage and testing
def test_arima_forecaster():
    """Test the ARIMA forecaster with synthetic data"""
    # Generate synthetic time series data
    np.random.seed(42)
    n_points = 100
    
    # Create trend + seasonality + noise
    trend = np.linspace(0, 10, n_points)
    seasonality = 5 * np.sin(2 * np.pi * np.arange(n_points) / 12)
    noise = np.random.normal(0, 1, n_points)
    
    data = trend + seasonality + noise
    
    # Initialize forecaster
    forecaster = EnhancedARIMAForecaster({
        'min_history_length': 20,
        'forecast_horizon': 12,
        'confidence_level': 0.95,
        'auto_optimize': True
    })
    
    # Add data points
    for i, value in enumerate(data):
        forecaster.add_data_point(value, f"2024-{i//30+1:02d}-{i%30+1:02d}")
    
    # Generate forecast
    result = forecaster.forecast(steps=12)
    
    print("Forecast Results:")
    print(f"Forecast values: {result.forecast}")
    print(f"Model AIC: {result.model_aic:.3f}")
    print(f"Model BIC: {result.model_bic:.3f}")
    
    # Get scaling recommendations
    recommendations = forecaster.get_scaling_recommendations(current_load=0.7, threshold=0.8)
    print(f"Scaling recommendation: {recommendations['action']}")
    print(f"Reason: {recommendations['reason']}")
    
    # Plot results
    forecaster.plot_forecast('test_forecast.png')
    
    return forecaster

if __name__ == "__main__":
    test_arima_forecaster()
