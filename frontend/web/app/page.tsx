'use client'

import { useEffect, useMemo, useState } from 'react'

interface ListingItem {
  id: string
  title: string
  price: number
  mileage: number
  year: number
  make: string
  model: string
  transmission: string
  fuelType: string
  bodyType: string
  condition: string
  image: string
  location: string
  description: string
  pivotScore: number
  marketSentiment: string
  viewsCount: number
}

interface PivotScoreData {
  pivotScore: number
  confidence: number
  smartBuyIndex: number
  riskRating: string
}

interface FuelPrediction {
  litersPerHundredKm: number
  monthlyBudgetUgx: number
  annualCostUgx: number
}

interface LogisticsQuote {
  distanceKm: number
  estimatedDurationHours: number
  totalPrice: number
  roadCondition: string
}

interface ResaleForecast {
  currentValue: number
  forecastedValueUgx: number
  depreciationPercent: number
}

const placeholderImage = '/images/car-placeholder.svg'
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const PAYMENT_URL = process.env.NEXT_PUBLIC_PAYMENT_URL || 'http://localhost:8007'
const LOGISTICS_URL = process.env.NEXT_PUBLIC_LOGISTICS_URL || 'http://localhost:8003'

const UGX_TO_USD = 3700 // Current rate

function formatCurrency(amount: number, currency: 'UGX' | 'USD' = 'UGX'): string {
  if (currency === 'USD') {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount / UGX_TO_USD)
  }
  return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX' }).format(amount)
}

function mapApiListing(item: any): ListingItem {
  const make = (item.vehicle_make ?? 'unknown').toString()
  const model = (item.vehicle_model ?? 'unknown').toString()

  const normalize = (s: string) =>
    s
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '')

  const filename = `${normalize(make)}-${normalize(model)}.svg`
  const localImage = `/images/${filename}`

  return {
    id: item.id ?? `${make}-${model}-${item.vehicle_year}`,
    title: `${item.vehicle_year ?? ''} ${make} ${model}`.trim(),
    price: item.listing_price ?? 0,
    mileage: item.vehicle_mileage_km ?? 0,
    year: item.vehicle_year ?? 0,
    make,
    model,
    transmission: item.transmission ?? 'Automatic',
    fuelType: item.fuel_type ?? 'Petrol',
    bodyType: item.body_type ?? 'SUV',
    condition: item.listing_status ?? 'Active',
    image: localImage,
    location: item.location ?? 'Kampala, UG',
    description: item.description ?? 'Well-maintained used car with local transport options.',
    pivotScore: item.pivot_score ?? Math.max(55, Math.min(95, 75 + Math.floor(Math.random() * 15))),
    marketSentiment: item.market_sentiment ?? 'positive',
    viewsCount: item.views_count ?? Math.floor(500 + Math.random() * 1500),
  }
}

function PivotScoreBadge({ score, sentiment }: { score: number; sentiment: string }) {
  const getColor = () => {
    if (score >= 80) return 'bg-green-100 text-green-800 border-green-300'
    if (score >= 60) return 'bg-amber-100 text-amber-800 border-amber-300'
    return 'bg-red-100 text-red-800 border-red-300'
  }

  const getSentiment = () => {
    if (sentiment === 'positive') return '🔥 Great Deal!'
    if (sentiment === 'stable') return '✅ Fair Price'
    return '⚠️ Consider'
  }

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-bold border ${getColor()}`}>
      <span>Pivot: {Math.round(score)}/100</span>
      <span className="text-xs">{getSentiment()}</span>
    </div>
  )
}

export default function HomePage() {
  const [listings, setListings] = useState<ListingItem[]>([])
  const [selectedCar, setSelectedCar] = useState<ListingItem | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currency, setCurrency] = useState<'UGX' | 'USD'>('UGX')
  const [priceRange, setPriceRange] = useState('all')
  const [bodyTypeFilter, setBodyTypeFilter] = useState('all')
  const [fuelTypeFilter, setFuelTypeFilter] = useState('all')
  const [transmissionFilter, setTransmissionFilter] = useState('all')
  const [sortBy, setSortBy] = useState('newest')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pivotData, setPivotData] = useState<PivotScoreData | null>(null)
  const [fuelPrediction, setFuelPrediction] = useState<FuelPrediction | null>(null)
  const [logisticsQuote, setLogisticsQuote] = useState<LogisticsQuote | null>(null)
  const [resaleForecast, setResaleForecast] = useState<ResaleForecast | null>(null)
  const [fuelPrice, setFuelPrice] = useState<{ petrol: number; diesel: number } | null>(null)
  const [paymentMethod, setPaymentMethod] = useState<'bank_transfer' | 'mobile_money' | 'card' | 'pay_later'>('bank_transfer')
  const [transactionStatus, setTransactionStatus] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    async function fetchListings() {
      try {
        const params = new URLSearchParams()
        params.append('limit', '100')
        if (sortBy !== 'newest') params.append('sort_by', sortBy)

        const response = await fetch(`${apiUrl}/api/v1/listings?${params.toString()}`, {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(`Failed to load listings: ${response.status}`)
        }

        const data = await response.json()
        const items = Array.isArray(data.items) ? data.items.map(mapApiListing) : []

        if (items.length === 0) {
          setError('No listings available at the moment.')
        } else {
          setError(null)
        }

        setListings(items)
      } catch (fetchError) {
        console.error(fetchError)
        setError('Could not reach the backend API.')
        setListings([])
      } finally {
        setLoading(false)
      }
    }

    fetchListings()

    return () => {
      controller.abort()
    }
  }, [sortBy])

  // Fetch Pivot Score when car selected
  useEffect(() => {
    if (!selectedCar) {
      setPivotData(null)
      setFuelPrediction(null)
      setLogisticsQuote(null)
      return
    }

    const car = selectedCar

    async function fetchScores() {
      try {
        // Fetch Pivot Score
        const scoreRes = await fetch(
          `${apiUrl}/api/v1/scores/pivot?vehicle_make=${car.make}&vehicle_model=${car.model}&vehicle_year=${car.year}&vehicle_mileage_km=${car.mileage}&listing_price=${car.price}`
        )
        if (scoreRes.ok) {
          const scoreData = await scoreRes.json()
          setPivotData(scoreData.data)
        }

        // Fetch Fuel Prediction
        const fuelRes = await fetch(
          `${apiUrl}/api/v1/insights/fuel-prediction?vehicle_make=${car.make}&vehicle_model=${car.model}&vehicle_year=${car.year}&transmission=${car.transmission.toLowerCase()}`
        )
        if (fuelRes.ok) {
          const fuelData = await fuelRes.json()
          setFuelPrediction({
            litersPerHundredKm: fuelData.data.liters_per_100km,
            monthlyBudgetUgx: fuelData.data.monthly_fuel_budget_ugx,
            annualCostUgx: fuelData.data.annual_fuel_cost_ugx,
          })
        }

        // Fetch Resale Forecast
        const resaleRes = await fetch(
          `${apiUrl}/api/v1/insights/resale-forecast?vehicle_make=${car.make}&vehicle_model=${car.model}&vehicle_year=${car.year}&current_price=${car.price}&months_ahead=24`
        )
        if (resaleRes.ok) {
          const resaleData = await resaleRes.json()
          setResaleForecast({
            currentValue: resaleData.data.current_value_ugx,
            forecastedValueUgx: resaleData.data.forecasted_value_ugx,
            depreciationPercent: resaleData.data.depreciation_percent,
          })
        }

        // Fetch current fuel price from logistics service
        const fuelPriceRes = await fetch(`${LOGISTICS_URL}/api/v1/logistics/fuel-price`)
        if (fuelPriceRes.ok) {
          const fuelPriceData = await fuelPriceRes.json()
          setFuelPrice({
            petrol: fuelPriceData.data.petrol_per_liter_ugx,
            diesel: fuelPriceData.data.diesel_per_liter_ugx,
          })
        }
      } catch (err) {
        console.error('Error fetching scores:', err)
      }
    }

    fetchScores()
  }, [selectedCar])

  const results = useMemo(
    () =>
      listings.filter((car) => {
        const query = searchTerm.toLowerCase()
        const matchesSearch =
          car.title.toLowerCase().includes(query) ||
          car.make.toLowerCase().includes(query) ||
          car.model.toLowerCase().includes(query)

        const matchesPrice =
          priceRange === 'all' ||
          (priceRange === 'budget' && car.price < 6_000_000) ||
          (priceRange === 'mid' && car.price >= 6_000_000 && car.price < 12_000_000) ||
          (priceRange === 'premium' && car.price >= 12_000_000)

        const matchesBodyType =
          bodyTypeFilter === 'all' || car.bodyType.toLowerCase() === bodyTypeFilter.toLowerCase()

        const matchesFuelType =
          fuelTypeFilter === 'all' || car.fuelType.toLowerCase() === fuelTypeFilter.toLowerCase()

        const matchesTransmission =
          transmissionFilter === 'all' ||
          car.transmission.toLowerCase() === transmissionFilter.toLowerCase()

        return (
          matchesSearch &&
          matchesPrice &&
          matchesBodyType &&
          matchesFuelType &&
          matchesTransmission
        )
      }),
    [listings, searchTerm, priceRange, bodyTypeFilter, fuelTypeFilter, transmissionFilter]
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-indigo-700">AutoPivot</h1>
            <p className="text-sm text-gray-600">Uganda's AI-powered vehicle marketplace</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => setCurrency(currency === 'UGX' ? 'USD' : 'UGX')}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold"
            >
              {currency}
            </button>
            <a
              href={`${apiUrl}`}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
            >
              API
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Search & Filters */}
        {!selectedCar && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Find Your Perfect Vehicle</h2>

            <div className="mb-6">
              <input
                type="search"
                placeholder="Search by make, model, or features..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Price Range (UGX)</label>
                <select
                  value={priceRange}
                  onChange={(e) => setPriceRange(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="all">All Prices</option>
                  <option value="budget">Budget (&lt; 6M)</option>
                  <option value="mid">Mid-Range (6M - 12M)</option>
                  <option value="premium">Premium (&gt; 12M)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Body Type</label>
                <select
                  value={bodyTypeFilter}
                  onChange={(e) => setBodyTypeFilter(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="all">All Types</option>
                  <option value="sedan">Sedan</option>
                  <option value="suv">SUV</option>
                  <option value="hatchback">Hatchback</option>
                  <option value="van">Van</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Fuel Type</label>
                <select
                  value={fuelTypeFilter}
                  onChange={(e) => setFuelTypeFilter(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="all">All Fuels</option>
                  <option value="petrol">Petrol</option>
                  <option value="diesel">Diesel</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Transmission</label>
                <select
                  value={transmissionFilter}
                  onChange={(e) => setTransmissionFilter(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="all">All Transmissions</option>
                  <option value="manual">Manual</option>
                  <option value="automatic">Automatic</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Sort By</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="newest">Newest First</option>
                  <option value="cheapest">Cheapest First</option>
                  <option value="most_popular">Most Popular</option>
                  <option value="best_value">Best Value (Pivot Score)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Results Count & Loading */}
        <div className="mb-6">
          <h3 className="text-lg font-bold text-gray-800">
            {results.length} vehicle{results.length === 1 ? '' : 's'} found
          </h3>
          {loading && <p className="text-gray-600">Loading latest listings...</p>}
          {error && <p className="text-red-600 font-bold">⚠️ {error}</p>}
        </div>

        {/* Detail View */}
        {selectedCar ? (
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <button
              onClick={() => setSelectedCar(null)}
              className="m-6 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-bold"
            >
              ← Back to Listings
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8">
              {/* Image Section */}
              <div>
                <img
                  src={selectedCar.image}
                  alt={selectedCar.title}
                  className="w-full rounded-lg shadow-lg mb-6"
                  onError={(e) => {
                    const t = e.target as HTMLImageElement
                    if (t.src !== placeholderImage) t.src = placeholderImage
                  }}
                />
              </div>

              {/* Details Section */}
              <div>
                <h2 className="text-3xl font-bold text-gray-800 mb-4">{selectedCar.title}</h2>

                {/* Pivot Score */}
                <div className="mb-6 p-4 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg">
                  <PivotScoreBadge score={selectedCar.pivotScore} sentiment={selectedCar.marketSentiment} />
                  {pivotData && (
                    <div className="mt-4 text-sm text-gray-700">
                      <p>✅ Confidence: {Math.round(pivotData.confidence * 100)}%</p>
                      <p>⚠️ Risk: {pivotData.riskRating}</p>
                    </div>
                  )}
                </div>

                {/* Price */}
                <div className="mb-6 p-4 bg-green-100 rounded-lg border-2 border-green-300">
                  <div className="text-4xl font-bold text-green-800">
                    {formatCurrency(selectedCar.price, currency)}
                  </div>
                  <p className="text-sm text-green-700 mt-2">
                    {currency === 'UGX'
                      ? `≈ ${formatCurrency(selectedCar.price, 'USD')}`
                      : `≈ ${formatCurrency(selectedCar.price, 'UGX')}`}
                  </p>
                </div>

                {/* Specifications */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <p className="text-xs text-gray-600">Year</p>
                    <p className="text-lg font-bold">{selectedCar.year}</p>
                  </div>
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <p className="text-xs text-gray-600">Mileage</p>
                    <p className="text-lg font-bold">{selectedCar.mileage.toLocaleString()} km</p>
                  </div>
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <p className="text-xs text-gray-600">Body Type</p>
                    <p className="text-lg font-bold">{selectedCar.bodyType}</p>
                  </div>
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <p className="text-xs text-gray-600">Transmission</p>
                    <p className="text-lg font-bold">{selectedCar.transmission}</p>
                  </div>
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <p className="text-xs text-gray-600">Fuel Type</p>
                    <p className="text-lg font-bold">{selectedCar.fuelType}</p>
                  </div>
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <p className="text-xs text-gray-600">Views</p>
                    <p className="text-lg font-bold">{selectedCar.viewsCount}</p>
                  </div>
                </div>

                <div className="mb-6">
                  <p className="text-sm text-gray-600">{selectedCar.description}</p>
                </div>

                {/* Fuel Prediction */}
                {fuelPrediction && (
                  <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h3 className="font-bold text-yellow-800 mb-3">⛽ Fuel Economy Estimate</h3>
                    <p className="text-sm text-yellow-700">
                      {fuelPrediction.litersPerHundredKm.toFixed(1)} L/100km
                    </p>
                    <p className="text-sm text-yellow-700">
                      Monthly budget: {formatCurrency(fuelPrediction.monthlyBudgetUgx, 'UGX')}
                    </p>
                    <p className="text-sm text-yellow-700">
                      Annual cost: {formatCurrency(fuelPrediction.annualCostUgx, 'UGX')}
                    </p>
                  </div>
                )}

                {resaleForecast && (
                  <div className="mb-6 p-4 bg-slate-50 border border-slate-200 rounded-lg">
                    <h3 className="font-bold text-slate-800 mb-3">📈 Resale Forecast (24 months)</h3>
                    <p className="text-sm text-slate-700">
                      Current value: {formatCurrency(resaleForecast.currentValue, 'UGX')}
                    </p>
                    <p className="text-sm text-slate-700">
                      Forecasted value: {formatCurrency(resaleForecast.forecastedValueUgx, 'UGX')}
                    </p>
                    <p className="text-sm text-slate-700">
                      Depreciation: {resaleForecast.depreciationPercent}%
                    </p>
                  </div>
                )}

                {fuelPrice && (
                  <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                    <h3 className="font-bold text-emerald-800 mb-3">⛽ Current Fuel Price</h3>
                    <p className="text-sm text-emerald-700">Petrol: {formatCurrency(fuelPrice.petrol, 'UGX')} / L</p>
                    <p className="text-sm text-emerald-700">Diesel: {formatCurrency(fuelPrice.diesel, 'UGX')} / L</p>
                  </div>
                )}

                {/* Call-to-Action */}
                <div className="mb-6">
                  <h4 className="font-bold mb-2">Preferred Payment</h4>
                  <div className="flex gap-3 mb-3">
                    <button
                      onClick={() => setPaymentMethod('bank_transfer')}
                      className={`px-4 py-2 rounded-lg font-bold ${paymentMethod === 'bank_transfer' ? 'bg-green-600 text-white' : 'bg-gray-100'}`}>
                      🏦 Bank Transfer
                    </button>
                    <button
                      onClick={() => setPaymentMethod('mobile_money')}
                      className={`px-4 py-2 rounded-lg font-bold ${paymentMethod === 'mobile_money' ? 'bg-green-600 text-white' : 'bg-gray-100'}`}>
                      📱 Mobile Money
                    </button>
                    <button
                      onClick={() => setPaymentMethod('card')}
                      className={`px-4 py-2 rounded-lg font-bold ${paymentMethod === 'card' ? 'bg-gray-800 text-white' : 'bg-gray-100'}`}>
                      💳 Card
                    </button>
                  </div>

                  <div className="flex gap-4">
                    <button
                      onClick={async () => {
                        try {
                          setTransactionStatus('initiating')
                          const url = `${PAYMENT_URL}/api/v1/transactions/initiate?listing_id=${encodeURIComponent(selectedCar.id)}&buyer_id=buyer-1&payment_method=${paymentMethod}`
                          const res = await fetch(url, { method: 'POST' })
                          if (!res.ok) throw new Error('Payment service error')
                          const body = await res.json()
                          setTransactionStatus(`success: ${body.transaction.transaction_id}`)
                        } catch (err) {
                          console.error(err)
                          setTransactionStatus('failed')
                        }
                      }}
                      className="flex-1 px-6 py-3 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-700"
                    >
                      💸 Initiate Payment
                    </button>
                    <button className="flex-1 px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700">
                      🔍 Request Inspection
                    </button>
                  </div>

                  {transactionStatus && <p className="mt-3 text-sm">Status: {transactionStatus}</p>}
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Listings Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.length > 0 ? (
              results.map((car) => (
                <div
                  key={car.id}
                  onClick={() => setSelectedCar(car)}
                  className="bg-white rounded-xl shadow-md hover:shadow-lg transition cursor-pointer overflow-hidden"
                >
                  <div className="relative">
                    <img
                      src={car.image}
                      alt={car.title}
                      className="w-full h-48 object-cover"
                      onError={(e) => {
                        const t = e.target as HTMLImageElement
                        if (t.src !== placeholderImage) t.src = placeholderImage
                      }}
                    />
                    <div className="absolute top-3 right-3">
                      <PivotScoreBadge score={car.pivotScore} sentiment={car.marketSentiment} />
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="font-bold text-lg text-gray-800">{car.title}</h3>
                    <p className="text-2xl font-bold text-green-600 my-2">
                      {formatCurrency(car.price, currency)}
                    </p>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>📍 {car.location}</p>
                      <p>🚗 {car.mileage.toLocaleString()} km • {car.year}</p>
                      <p>⚙️ {car.transmission} • {car.fuelType}</p>
                      <p>👁️ {car.viewsCount} views</p>
                    </div>
                    <button className="w-full mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold">
                      View Details
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <p className="text-gray-600 text-lg">No vehicles found matching your filters.</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 py-8 text-center">
          <p>AutoPivot Uganda © 2024 — AI-powered vehicle marketplace for East Africa</p>
        </div>
      </footer>
    </div>
  )
}
