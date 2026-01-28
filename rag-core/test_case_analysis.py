"""
Test de Análisis de Casos - Verificar capacidad del RAG
Este script prueba si el sistema puede analizar casos complejos, no solo consultas simples
"""
import requests
import json

RAG_URL = "http://localhost:8000/query"

# Casos de prueba
casos = [
    {
        "nombre": "Consulta Simple - Artículo Específico",
        "payload": {
            "question": "Que dice el articulo 10 de la constitucion",
            "category_ids": [1],
            "top_k": 5
        },
        "tipo": "simple"
    },
    {
        "nombre": "Análisis de Caso - Robo Agravado",
        "payload": {
            "question": """
            Tengo un caso donde el acusado ingresó a una vivienda durante la noche, 
            portando un arma blanca, y sustrajo objetos de valor por un monto de 15,000 Bs. 
            El propietario estaba presente y sufrió lesiones leves al intentar defenderse.
            
            ¿Qué artículos del código penal aplican a este caso? 
            ¿Cuál sería la pena probable considerando las agravantes?
            ¿Hay alguna circunstancia atenuante que podría aplicar?
            """,
            "category_ids": [2],  # Categoría Penal
            "top_k": 20  # Más contextos para análisis complejo
        },
        "tipo": "caso_complejo"
    },
    {
        "nombre": "Análisis de Caso - Violencia Doméstica",
        "payload": {
            "question": """
            Una mujer denuncia que su pareja la agredió físicamente en tres ocasiones 
            durante el último mes, causándole hematomas y una fractura en el brazo. 
            Hay testigos (vecinos) y certificado médico forense.
            
            ¿Qué leyes y artículos protegen a la víctima?
            ¿Qué medidas de protección se pueden solicitar?
            ¿Cuál es el procedimiento legal a seguir?
            """,
            "category_ids": [2],
            "top_k": 20
        },
        "tipo": "caso_complejo"
    },
    {
        "nombre": "Consulta General - Procedimiento",
        "payload": {
            "question": "Cuales son los pasos del proceso penal en Bolivia",
            "category_ids": [2],
            "top_k": 15
        },
        "tipo": "general"
    }
]

def test_caso(caso):
    """Prueba un caso individual"""
    print("\n" + "="*80)
    print(f"CASO: {caso['nombre']}")
    print(f"TIPO: {caso['tipo'].upper()}")
    print("="*80)
    
    try:
        response = requests.post(RAG_URL, json=caso['payload'], timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Respuesta recibida")
            print(f"Contextos encontrados: {data.get('num_contexts', 0)}")
            print(f"Fuentes: {', '.join(data.get('sources', []))}")
            
            print(f"\n📄 RESPUESTA DEL ASISTENTE:")
            print("-" * 80)
            print(data.get('answer', 'Sin respuesta'))
            print("-" * 80)
            
            # Evaluar calidad de la respuesta
            answer = data.get('answer', '')
            
            if caso['tipo'] == 'simple':
                # Para consultas simples, verificar que mencione el artículo
                if 'artículo' in answer.lower() or 'articulo' in answer.lower():
                    print("\n✅ EVALUACIÓN: Respuesta contiene referencia a artículos")
                else:
                    print("\n⚠️ EVALUACIÓN: Respuesta no menciona artículos específicos")
            
            elif caso['tipo'] == 'caso_complejo':
                # Para casos complejos, verificar análisis detallado
                criterios = {
                    'menciona_articulos': any(x in answer.lower() for x in ['artículo', 'articulo', 'ley']),
                    'menciona_penas': any(x in answer.lower() for x in ['pena', 'sanción', 'años', 'prisión']),
                    'analisis_detallado': len(answer) > 300,
                    'menciona_procedimiento': any(x in answer.lower() for x in ['procedimiento', 'proceso', 'denuncia'])
                }
                
                print(f"\n📊 EVALUACIÓN DEL ANÁLISIS:")
                for criterio, cumple in criterios.items():
                    status = "✅" if cumple else "❌"
                    print(f"   {status} {criterio.replace('_', ' ').title()}")
                
                if all(criterios.values()):
                    print("\n✅ CONCLUSIÓN: El sistema puede analizar casos complejos")
                else:
                    print("\n⚠️ CONCLUSIÓN: El análisis podría mejorar")
            
            return True
            
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("TEST DE CAPACIDADES DEL RAG - CONSULTAS SIMPLES VS ANÁLISIS DE CASOS")
    print("="*80)
    
    resultados = {
        "exitosos": 0,
        "fallidos": 0
    }
    
    for caso in casos:
        success = test_caso(caso)
        if success:
            resultados["exitosos"] += 1
        else:
            resultados["fallidos"] += 1
        
        input("\nPresiona Enter para continuar con el siguiente caso...")
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    print(f"Total casos probados: {len(casos)}")
    print(f"✅ Exitosos: {resultados['exitosos']}")
    print(f"❌ Fallidos: {resultados['fallidos']}")
    print("="*80)
    
    if resultados['fallidos'] == 0:
        print("\n🎉 El sistema RAG puede manejar tanto consultas simples como análisis de casos")
    else:
        print(f"\n⚠️ Revisar los {resultados['fallidos']} casos fallidos")

if __name__ == "__main__":
    main()
