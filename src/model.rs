// TODO: make this pluggable? feature-flag?
use rustc_hash::FxHashMap;

use crate::agent::{ AgentFactory, Agent };
use crate::datadict::DataDict;
use crate::operation::Operation;


/// Main API (rough outline)
/// TODO: add PyO3 types
/// TODO: read krABMaga code
trait ModelFrame<'a> {
    fn new(
        parameters: FxHashMap<&'a str, &'a str>,
        _run_id: Option<usize>,
        forwarded_args: FxHashMap<&'a str, &'a str>,
    ) -> Self;
    fn stop();
}

pub struct Model<'a> {
    name: String,
    parameters: FxHashMap<&'a str, f64>,
    agent_list: Vec<Box<Agent<'a>>>,
}

pub struct ModelBuilder<'a> {
    name: String,
    parameters: Option<FxHashMap<&'a str, f64>>,
    // Will first assume that we have a homogeneous list of agents
    // TODO: add in capability for multiple types of agents (using multiple AgentFactories)
    // agent_list: Vec<Agent<'a>>,
    init_prop: Option<FxHashMap<&'a str, i64>>,
    operations: Option<Vec<Operation<'a>>>,
    // TODO: typed-builder? -> want to add operations and then create the factory, and then you can build
    agent_factory: Option<AgentFactory<'a>>,
}

impl<'a> Model<'_> {
    pub fn builder(name: String) -> ModelBuilder<'static> {
        ModelBuilder::new(name)
    }

    pub fn run(self) -> DataDict<'a> {
        DataDict::new()
    }
}

// TODO: builder should accept Python equivalents
impl<'a> ModelBuilder<'a> {
    fn new(name: String) -> Self {
        Self {
            name,
            parameters: None,
            init_prop: None,
            operations: None,
            agent_factory: None,
        }
    }

    // fn build(self) -> Model<'a> {
    //     let agent_factory = self.agent_factory.unwrap();
    //     Model {
    //         name: self.name,
    //         parameters: self.parameters.unwrap(),
    //         agent_list: vec![agent_factory.create_agent()],
    //     }
    // }
}
